"""
Voice Activity Detection (VAD) & Barge-In Interruption Engine.
Processes streaming 20ms audio frames, detects speech onset/offset, and triggers barge-in events.
"""

from typing import Callable, Optional
from .audio_utils import AudioUtils


class VoiceActivityDetector:
    """
    Stateful Voice Activity Detector with Barge-In detection for telephony audio.
    """

    def __init__(
        self,
        energy_threshold: float = 450.0,
        speech_onset_frames: int = 3,      # ~60ms of speech to trigger onset
        silence_cutoff_frames: int = 18,    # ~360ms of silence to trigger end-of-turn
        on_barge_in: Optional[Callable[[], None]] = None,
    ):
        self.energy_threshold = energy_threshold
        self.speech_onset_frames = speech_onset_frames
        self.silence_cutoff_frames = silence_cutoff_frames
        self.on_barge_in = on_barge_in

        # Internal state
        self.is_speaking = False
        self.consecutive_speech_frames = 0
        self.consecutive_silence_frames = 0
        self.is_agent_speaking = False
        self.accumulated_pcm_speech = bytearray()

    def set_agent_speaking_state(self, speaking: bool) -> None:
        """Inform VAD whether the AI agent is currently playing voice audio to the caller."""
        self.is_agent_speaking = speaking

    def process_frame(self, mulaw_frame: bytes) -> dict:
        """
        Process a 20ms mulaw audio frame (160 bytes at 8000Hz).
        Returns a dict indicating state transitions:
        {
            "is_speech": bool,
            "speech_started": bool,
            "speech_ended": bool,
            "barge_in_triggered": bool,
            "energy": float,
            "audio_pcm": bytes,
        }
        """
        pcm16 = AudioUtils.mulaw_to_pcm16(mulaw_frame)
        energy = AudioUtils.calculate_rms_energy(pcm16)

        is_voice_energy = energy >= self.energy_threshold
        speech_started = False
        speech_ended = False
        barge_in_triggered = False

        if is_voice_energy:
            self.consecutive_speech_frames += 1
            self.consecutive_silence_frames = 0
            self.accumulated_pcm_speech.extend(pcm16)

            # Check if caller speech onset reached
            if not self.is_speaking and self.consecutive_speech_frames >= self.speech_onset_frames:
                self.is_speaking = True
                speech_started = True

            # Check Barge-In (Caller interrupted AI agent while AI was speaking)
            if self.is_agent_speaking and self.consecutive_speech_frames >= 2:
                barge_in_triggered = True
                if self.on_barge_in:
                    try:
                        self.on_barge_in()
                    except Exception:
                        pass
        else:
            self.consecutive_silence_frames += 1
            if self.is_speaking:
                self.accumulated_pcm_speech.extend(pcm16)
                if self.consecutive_silence_frames >= self.silence_cutoff_frames:
                    # Caller finished speaking their sentence/turn
                    self.is_speaking = False
                    speech_ended = True
                    self.consecutive_speech_frames = 0

        result_pcm = bytes(self.accumulated_pcm_speech) if speech_ended else b""
        if speech_ended:
            self.accumulated_pcm_speech.clear()

        return {
            "is_speech": self.is_speaking or is_voice_energy,
            "speech_started": speech_started,
            "speech_ended": speech_ended,
            "barge_in_triggered": barge_in_triggered,
            "energy": energy,
            "speech_pcm": result_pcm,
        }

    def reset(self) -> None:
        """Reset internal frame counters and buffers."""
        self.is_speaking = False
        self.consecutive_speech_frames = 0
        self.consecutive_silence_frames = 0
        self.accumulated_pcm_speech.clear()
