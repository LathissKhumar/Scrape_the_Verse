import uvicorn
from app.config.settings import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
