from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HONU_MCP_HOST: str
    NEAR_MCP_URL: str
    GENERATED_IMAGE_BUCKET_NAME: str
    GCP_PROJECT: str


AgentSettings = Settings()
