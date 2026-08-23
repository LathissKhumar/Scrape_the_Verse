"""
Audio Utilities for Voice Agent & Twilio Media Streams.
Handles 8000Hz mulaw codec, 16kHz PCM resampling, base64 framing, and RMS audio energy.
"""

import base64
from typing import Tuple
import audioop


class AudioUtils:
    """Audio converter and framing utilities for telephony audio."""

    @staticmethod
    def base64_to_mulaw(payload: str) -> bytes:
        """Decode base64 string from Twilio media stream into raw 8kHz mulaw bytes."""
        return base64.b64decode(payload)

    @staticmethod
    def mulaw_to_base64(mulaw_bytes: bytes) -> str:
        """Encode raw 8kHz mulaw bytes into base64 string for Twilio media stream."""
        return base64.b64encode(mulaw_bytes).decode("utf-8")

    @staticmethod
    def mulaw_to_pcm16(mulaw_bytes: bytes) -> bytes:
        """Convert 8000Hz 8-bit mulaw audio to 8000Hz 16-bit linear PCM."""
        return audioop.ulaw2lin(mulaw_bytes, 2)

    @staticmethod
    def pcm16_to_mulaw(pcm_bytes: bytes) -> bytes:
        """Convert 8000Hz 16-bit linear PCM audio to 8000Hz 8-bit mulaw."""
        return audioop.lin2ulaw(pcm_bytes, 2)

    @staticmethod
    def resample(pcm_bytes: bytes, in_rate: int = 8000, out_rate: int = 16000) -> bytes:
        """
        Resample 16-bit mono PCM audio between sample rates.
        Returns resampled PCM bytes.
        """
        if in_rate == out_rate or not pcm_bytes:
            return pcm_bytes
        converted, _ = audioop.ratecv(pcm_bytes, 2, 1, in_rate, out_rate, None)
        return converted

    @staticmethod
    def calculate_rms_energy(pcm_bytes: bytes) -> float:
        """Calculate Root Mean Square (RMS) energy level of 16-bit linear PCM audio."""
        if not pcm_bytes:
            return 0.0
        try:
            return float(audioop.rms(pcm_bytes, 2))
        except Exception:
            return 0.0

    @staticmethod
    def create_silence_mulaw(duration_ms: int = 20) -> bytes:
        """Generate silent mulaw audio chunk for a given duration (default 20ms = 160 bytes at 8kHz)."""
        num_samples = int((8000 * duration_ms) / 1000)
        # 0xFF in mulaw represents 0 linear amplitude (silence)
        return b"\xff" * num_samples
