"""
Voice Agent Microservice CLI Runner (Port 8084).
Launch with: python -m MicroServices.Voice_Agent.run
"""

import os

import uvicorn

PORT = int(os.environ.get("VOICE_AGENT_PORT", "8084"))


def main():
    print(f"Starting Voice Agent Microservice on port {PORT}...")
    uvicorn.run(
        "MicroServices.Voice_Agent.server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
