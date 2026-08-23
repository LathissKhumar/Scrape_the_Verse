# Communication Service (IMAP IDLE + SMTP)

A zero-cloud, high-efficiency email communication microservice for **AgencyOS**, replacing Google Cloud Pub/Sub with **IMAP IDLE** and **Gmail SMTP**.

---

## 1. Architecture Overview

```text
                           ┌──────────────────────┐
                           │      GMAIL           │
                           │                      │
                           │   IMAP / SMTP        │
                           └─────────┬────────────┘
                                     │
                        IMAP over TLS │ SMTP over TLS
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │     COMMUNICATION SERVICE      │
                    │             :8083              │
                    │                                │
                    │  ┌──────────────────────────┐  │
                    │  │     IMAP LISTENER        │  │
                    │  │                          │  │
                    │  │ CONNECT → AUTH → SELECT │  │
                    │  │           ↓              │  │
                    │  │          IDLE            │  │
                    │  │           ↓              │  │
                    │  │         EXISTS           │  │
                    │  └─────────────┬────────────┘  │
                    │                │               │
                    │                ▼               │
                    │       MESSAGE SYNCHRONIZER     │
                    │                │               │
                    │                ▼               │
                    │          MIME PARSER           │
                    │                │               │
                    │                ▼               │
                    │        THREAD CORRELATOR        │
                    │                │               │
                    │                ▼               │
                    │       INTENT CLASSIFIER        │
                    │                │               │
                    │          ┌─────┴─────┐         │
                    │          ▼           ▼         │
                    │       RULES        OLLAMA      │
                    │                      │          │
                    │                      ▼          │
                    │                  QWEN3          │
                    │          ┌──────────┴────────┐  │
                    │          ▼                   ▼  │
                    │      EVENT STORE         EVENT BUS
                    │          │                   │
                    └──────────┼───────────────────┘
                               │
                          A2A / HTTP
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
      ┌─────────────────┐               ┌─────────────────┐
      │  LEAD MANAGER   │               │       SDR       │
      │      :8082      │               │      :8084      │
      └─────────────────┘               └─────────────────┘
```

---

## 2. Key Features

- **IMAP IDLE Event-Driven Ingestion**: Real-time push notifications (`EXISTS`) without wasteful polling.
- **Thread-Aware SMTP Dispatch**: Outbound replies automatically maintain `In-Reply-To` and `References` headers.
- **MIME Parsing**: Handles multipart emails, attachments, international RFC 2047 subjects, plain text and HTML.
- **Thread Correlation**: Correlates conversations by headers and cleaned subjects.
- **Two-Tier Intent Classification**:
  - Fast deterministic rules for `OUT_OF_OFFICE`, `UNSUBSCRIBE`, `BOUNCE`, `REQUEST_MEETING`, `REQUEST_PRICING`.
  - Local Ollama/Qwen LLM fallback for ambiguous emails.
- **Durable SQLite Persistence**: 7 tables tracking accounts, mailbox state cursors, messages, threads, classifications, events, and outbound messages.
- **A2A Agent Card**: Discovery card exposed at `/.well-known/agent-card.json`.

---

## 3. Quick Start

### 1. Setup Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your Gmail details:
```env
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Service
```bash
uvicorn app.main:app --port 8083 --reload
```

---

## 4. API Endpoints

- `GET /health` - Service health and IMAP connection status
- `GET /api/v1/mailbox/status` - Current mailbox cursor and sync state
- `POST /api/v1/mailbox/sync` - Trigger incremental sync
- `GET /api/v1/messages` - List all ingested messages
- `GET /api/v1/threads/{thread_id}` - Conversation timeline with inbound and outbound messages
- `POST /api/v1/mail/send` - Send an outbound email or reply
- `GET /api/v1/events` - Query event store log
- `GET /.well-known/agent-card.json` - A2A agent discovery card

---

## 5. Running Automated Tests

```bash
pytest tests/ -v
```
