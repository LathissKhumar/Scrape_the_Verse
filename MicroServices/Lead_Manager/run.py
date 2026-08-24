"""
Lead Manager CLI Runner (Port 8082).
Launch with: python -m MicroServices.Lead_Manager.run
"""

import uvicorn

from .config.settings import get_settings

settings = get_settings()
PORT = settings.LEAD_MANAGER_API_PORT


def main():
    print(f"Starting Lead Manager Microservice on port {PORT}...")
    uvicorn.run(
        "MicroServices.Lead_Manager.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
