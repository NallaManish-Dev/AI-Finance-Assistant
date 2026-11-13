import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application settings read from the local environment."""

    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'ai_finance_assistant')
    MONGODB_CONNECT_TIMEOUT_MS = 5000
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_EXPIRATION_HOURS = 24
