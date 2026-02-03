import os

import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.plugins import ReflectAndRetryToolPlugin
from honu_google_adk.agent_router.honu_router import HonuAgentRouter
from honu_google_adk.agent_router.plugins import HonuConversationPlugin
from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    PORT: int = 7999
    USE_DEV_UI: bool = False
    GOOGLE_API_KEY: str

Settings = _Settings()

SESSION_SERVICE_URI = f'postgresql://{Settings.POSTGRES_USER}:{Settings.POSTGRES_PASSWORD}@{Settings.POSTGRES_HOST}:{Settings.POSTGRES_PORT}/{Settings.POSTGRES_DB}'
os.environ.setdefault('GOOGLE_API_KEY', Settings.GOOGLE_API_KEY)

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))


def full_name(t) -> str:
    """returns a fully qualified name for a type"""
    return f"{t.__module__}.{t.__qualname__}"


# Call the function to get the FastAPI app instance
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=['*'],
    web=Settings.USE_DEV_UI,
    session_db_kwargs={'pool_pre_ping': True},
    extra_plugins=[
        full_name(HonuConversationPlugin),
        full_name(ReflectAndRetryToolPlugin),
    ],
)

honu_router = HonuAgentRouter('', Settings.PORT)
app.include_router(honu_router.agent_router)


if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=Settings.PORT)