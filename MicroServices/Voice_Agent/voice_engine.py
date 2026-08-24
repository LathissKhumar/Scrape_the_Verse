"""
Voice Synthesis & Transcription Engine for Production Voice Agent.
Ultra-realistic Neural Text-to-Speech (Edge-TTS) and real-time Speech-to-Text (STT).
"""

import asyncio
import subprocess
from collections.abc import AsyncGenerator

import edge_tts
import speech_recognition as sr

from .audio_utils import AudioUtils
from .config.settings import get_voice_settings


class VoiceEngine:
    """
    Voice Engine handling real-time audio synthesis (TTS) and transcription (STT).
    """

    def __init__(self, voice: str | None = None):
        self.settings = get_voice_settings()
        self.voice = voice or self.settings.VOICE_TTS_VOICE
        self.recognizer = sr.Recognizer()

    async def synthesize_to_mulaw(self, text: str, voice: str | None = None) -> bytes:
        """
        Synthesize text to 8000Hz 8-bit mulaw audio bytes using Edge-TTS and ffmpeg.
        """
        target_voice = voice or self.voice
        if not text or not text.strip():
            return b""

        # 1. Generate MP3 stream via Edge-TTS
        communicate = edge_tts.Communicate(text.strip(), target_voice)
        audio_chunks: list[bytes] = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        raw_mp3 = b"".join(audio_chunks)
        if not raw_mp3:
            return b""

        # 2. Transcode MP3 to 8000Hz mulaw (telephony standard) via ffmpeg
        loop = asyncio.get_running_loop()
        mulaw_bytes = await loop.run_in_executor(
            None,
            self._transcode_mp3_to_mulaw_sync,
            raw_mp3,
        )
        return mulaw_bytes

    def _transcode_mp3_to_mulaw_sync(self, raw_mp3: bytes) -> bytes:
        """Synchronous helper running ffmpeg pipe."""
        try:
            proc = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i",
                    "pipe:0",
                    "-f",
                    "mulaw",
                    "-ar",
                    "8000",
                    "-ac",
                    "1",
                    "pipe:1",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            mulaw_out, _ = proc.communicate(input=raw_mp3)
            return mulaw_out
        except Exception:
            return b""

    async def stream_speech_frames(
        self,
        text: str,
        frame_size: int = 160,  # 20ms at 8000Hz
        voice: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Synthesize text and stream 20ms base64-encoded mulaw frames for Twilio WebSocket.
        """
        mulaw_audio = await self.synthesize_to_mulaw(text=text, voice=voice)
        if not mulaw_audio:
            return

        total_bytes = len(mulaw_audio)
        offset = 0
        while offset < total_bytes:
            chunk = mulaw_audio[offset : offset + frame_size]
            if len(chunk) < frame_size:
                # Pad remaining bytes with silence
                chunk = chunk + AudioUtils.create_silence_mulaw(
                    20 - int(len(chunk) / 8)
                )
            yield AudioUtils.mulaw_to_base64(chunk)
            offset += frame_size
            # 20ms real-time pacing
            await asyncio.sleep(0.018)

    async def transcribe_pcm(self, pcm_bytes: bytes, sample_rate: int = 8000) -> str:
        """
        Transcribe linear 16-bit PCM speech into text.
        """
        if not pcm_bytes or len(pcm_bytes) < 1600:  # Ignore under 100ms
            return ""

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self._transcribe_sync,
            pcm_bytes,
            sample_rate,
        )

    def _transcribe_sync(self, pcm_bytes: bytes, sample_rate: int = 8000) -> str:
        """Synchronous speech recognition wrapper."""
        try:
            # Create AudioData object (sample_width=2 bytes for 16-bit PCM)
            audio_data = sr.AudioData(
                pcm_bytes, sample_rate=sample_rate, sample_width=2
            )
            text = self.recognizer.recognize_google(audio_data)
            return text.strip()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""
        except Exception:
            return ""
