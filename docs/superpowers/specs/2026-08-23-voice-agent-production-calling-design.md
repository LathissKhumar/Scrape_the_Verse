# Voice Agent Production-Ready Real PSTN Calling Design Specification

**Status**: APPROVED & ALIGNED VIA /grill-me  
**Date**: 2026-08-23  

---

## 1. System Architecture & Call Flow

```text
 ┌──────────────────────────┐
 │ USER'S PHYSICAL MOBILE   │
 │ (Personal Phone Number)  │
 └────────────▲─────────────┘
              │  Cellular PSTN Call Rings
 ┌────────────┴─────────────┐
 │       TWILIO CARRIER     │
 │ (Free Trial PSTN Gateway)│
 └────────────┬─────────────┘
              │ Bi-Directional WebSocket Media Stream (8000Hz mulaw)
              ▼
 ┌──────────────────────────────────────────────────────────────┐
 │             VOICE AGENT MICROSERVICE (:8084)                 │
 │                                                              │
 │  1. Twilio Call Initiator:                                   │
 │     `POST /api/v1/voice/call/initiate`                       │
 │     Trigger outbound PSTN call to target phone number        │
 │                                                              │
 │  2. TwiML Webhook & Media Stream Server:                     │
 │     `POST /api/v1/voice/twiml` ──► <Connect><Stream>         │
 │     `WEBSOCKET /api/v1/voice/stream`                         │
 │                                                              │
 │  3. Real-Time Audio Engine:                                  │
 │     • Audio Decoder: 8000Hz mulaw <-> PCM 16kHz             │
 │     • Voice Activity Detection (VAD) & Energy Detection      │
 │     • Barge-in Interruption Manager: Stops TTS on speech     │
 │     • Speech-to-Text (STT): Web-Audio / Whisper / Deepgram   │
 │     • Conversational Brain: Ollama (qwen3:8b) State Machine  │
 │     • Text-to-Speech (TTS): Edge-TTS / Piper Neural Voices   │
 │     • Audio Encoder: PCM -> 8000Hz mulaw -> base64 chunks   │
 │                                                              │
 │  4. Lead Manager Integration:                                │
 │     On call completion, dispatches transcript, interest score│
 │     and booked meeting to Lead Manager (:8082)               │
 └──────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Technical Components

### A. Twilio Call Controller & TwiML Gateway
- **Module**: `MicroServices/Voice_Agent/twilio_controller.py`
- **Responsibilities**:
  - Initiates outbound calls via Twilio REST API (`client.calls.create`).
  - Generates dynamic TwiML containing `<Connect><Stream url="wss://{PUBLIC_URL}/api/v1/voice/stream"/></Connect>`.
  - Handles Twilio status callbacks (`ringing`, `in-progress`, `completed`, `busy`, `no-answer`).

### B. Bi-Directional WebSocket Media Stream Engine
- **Module**: `MicroServices/Voice_Agent/media_stream.py`
- **Protocol**: Twilio Media Streams format:
  - Inbound events: `{"event": "start"}`, `{"event": "media", "media": {"payload": base64_mulaw}}`, `{"event": "stop"}`.
  - Outbound events: `{"event": "media", "streamSid": stream_sid, "media": {"payload": base64_mulaw}}`, `{"event": "clear", "streamSid": stream_sid}`.
- **Audio Processing**:
  - `audioop` / `scipy` / `numpy` conversion: `audioop.ulaw2lin` (8kHz 8-bit mulaw -> 8kHz 16-bit PCM) and resampling to 16kHz for STT.
  - `audioop.lin2ulaw` (16kHz PCM -> 8kHz mulaw) for outbound TTS audio.

### C. Voice Activity Detection (VAD) & Barge-In Handler
- **Module**: `MicroServices/Voice_Agent/vad.py`
- **Responsibilities**:
  - Detects when the user begins speaking during agent audio playback.
  - Instantly sends Twilio `{"event": "clear", "streamSid": stream_sid}` to clear the device audio buffer.
  - Flushes queued speech audio and switches state to active user listening.

### D. Natural Voice Synthesis (TTS) & STT
- **Module**: `MicroServices/Voice_Agent/voice_engine.py`
- **STT**: Transcribes incoming PCM audio chunks into text.
- **TTS**: Synthesizes agent response text into audio using `edge-tts` (Microsoft Neural voices like `en-US-JennyNeural` or `en-US-GuyNeural`), converts to 8kHz mulaw, and yields base64 frames.

### E. Conversational State Machine & LLM Integration
- **Module**: `MicroServices/Voice_Agent/state_machine.py`
- **States**: `OPENING` -> `PITCH` -> `FAQ_AND_OBJECTIONS` -> `MEETING_BOOKING` -> `CLOSING`.
- **Context Injection**: Uses prospect's company name, audit weaknesses, prompt pack, and agency offerings.
- **LLM**: Local Ollama `qwen3:8b` (with Gemini fallback).

### F. Lead Manager Auto-Handoff
- **Module**: `MicroServices/Voice_Agent/telephony_adapter.py`
- **Handoff**:
  - Automatically records full turn-by-turn transcript and logs into SQLite database.
  - Computes final disposition (`MEETING_BOOKED`, `INTERESTED`, `NOT_INTERESTED`).
  - Calls Lead Manager (`:8082`) `/api/v1/events` and `/api/v1/meetings`.

---

## 3. Environment & Configuration Variables

Added to `.env`:
```ini
# ------------------------------------------------------------------------------
# Voice Agent & Twilio PSTN Configuration
# ------------------------------------------------------------------------------
VOICE_AGENT_PORT=8084
VOICE_PUBLIC_BASE_URL=https://your-domain.ngrok-free.app
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
PERSONAL_MOBILE_NUMBER=+1234567890
VOICE_TTS_VOICE=en-US-JennyNeural
```
