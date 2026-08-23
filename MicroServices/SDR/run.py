"""
SDR Microservice CLI Runner (Port 8081).
Launch with: python -m MicroServices.SDR.run
"""

import os
import uvicorn

PORT = int(os.environ.get("SDR_API_PORT", "8081"))


def main():
    print(f"Starting SDR Microservice on port {PORT}...")
    uvicorn.run(
        "MicroServices.SDR.server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
