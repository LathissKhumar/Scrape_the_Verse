# Voice Agent Production Real Calling Implementation Plan

> **Goal**: Upgrade Voice Agent Microservice (:8084) from a simulation engine into a production-ready real PSTN calling system via Twilio Media Streams with bi-directional WebSocket audio streaming, real-time VAD & barge-in interruption, ultra-natural neural TTS (`edge-tts`), local LLM conversational brain (`qwen3:8b`), and automated Lead Manager CRM synchronization.

---

## User Review Required

> [!IMPORTANT]
> To receive calls on your personal physical phone number, you will enter your free Twilio credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `PERSONAL_MOBILE_NUMBER`) and public tunnel URL (`VOICE_PUBLIC_BASE_URL`) in `.env`.
> The system also includes an auto-tunnel launcher script (`scripts/start_voice_tunnel.sh`) using ngrok or localtunnel.

---

## Proposed Changes

### 1. Configuration & Dependencies
#### [MODIFY] `requirements.txt` / environment
- Add `twilio`, `edge-tts`, `audioop-lts` (or pure-python mulaw converter for Python 3.14), `numpy`, `scipy` as needed.
#### [MODIFY] `.env`
- Add Twilio & Voice Agent configuration keys.
#### [MODIFY] `MicroServices/Voice_Agent/config/settings.py`
- Add Twilio and voice audio streaming settings.

---

### 2. Audio Processing & Voice Engines
#### [NEW] `MicroServices/Voice_Agent/audio_utils.py`
- Pure Python & standard library mulaw 8000Hz encoding/decoding and PCM 16kHz resampling (compatible with Python 3.14).
- Base64 payload encoding for Twilio Media Streams.
#### [NEW] `MicroServices/Voice_Agent/vad.py`
- Energy-based Voice Activity Detection (VAD) and speech frame accumulation.
- Barge-in detection trigger to clear Twilio playback buffer immediately when caller interrupts.
#### [NEW] `MicroServices/Voice_Agent/voice_engine.py`
- Neural TTS synthesis using `edge-tts` (streaming audio chunks).
- Integration with Speech-to-Text (STT) transcription.

---

### 3. Twilio Controller & WebSocket Media Stream Handler
#### [NEW] `MicroServices/Voice_Agent/twilio_controller.py`
- Outbound call trigger via Twilio REST API (`client.calls.create`).
- TwiML generation with `<Connect><Stream url="wss://.../api/v1/voice/stream"/></Connect>`.
- Call status webhook handler (`ringing`, `in-progress`, `completed`, `busy`, `no-answer`).
#### [NEW] `MicroServices/Voice_Agent/media_stream.py`
- FastAPI WebSocket endpoint handler for `wss://{PUBLIC_URL}/api/v1/voice/stream`.
- Bidirectional stream loop:
  - Receives inbound audio -> VAD -> STT -> LLM Dialogue Engine -> Edge-TTS -> mulaw 8kHz -> Outbound WebSocket frames.
  - Sends `{"event": "clear"}` on barge-in.

---

### 4. Conversational Engine & Lead Manager Handoff
#### [MODIFY] `MicroServices/Voice_Agent/server.py`
- Expose `/api/v1/voice/call/initiate`, `/api/v1/voice/twiml`, `/api/v1/voice/status-callback`, `/api/v1/voice/stream` (WebSocket).
#### [MODIFY] `MicroServices/Voice_Agent/telephony_adapter.py`
- Enhance adapter to manage live Twilio call sessions, save full audio transcripts to SQLite, and dispatch meeting results to Lead Manager (`:8082`).

---

### 5. Automated Tests & Verification
#### [NEW] `MicroServices/Voice_Agent/tests/test_real_calling.py`
- Unit and integration tests for:
  1. Mulaw audio encoding/decoding and resampling.
  2. Twilio TwiML generation and outbound call payload.
  3. WebSocket media stream message protocol (`start`, `media`, `clear`, `stop`).
  4. VAD barge-in interruption logic.
  5. Complete live call flow and Lead Manager meeting dispatch.

---

## Verification Plan

### Automated Tests
- Run full pytest test suite:
  ```bash
  .venv/bin/pytest MicroServices/Voice_Agent/tests/ -v
  ```

### Manual Verification
1. Inspect Twilio outbound call initiate endpoint with curl:
   ```bash
   curl -X POST http://127.0.0.1:8084/api/v1/voice/call/initiate \
     -H "Content-Type: application/json" \
     -d '{"to_phone": "+1234567890", "company_name": "Apex Roofing Solutions", "contact_name": "Marcus Vance"}'
   ```
2. Test WebSocket Media Stream with simulated Twilio payload frames.
3. Verify live Lead Manager update and meeting calendar generation.
