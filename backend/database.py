"""MongoDB connection setup using Motor (async)."""
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv(Path(__file__).parent / ".env")

MONGO_URL: str = os.environ["MONGO_URL"]
DB_NAME: str = os.environ["DB_NAME"]

client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URL)
db: AsyncIOMotorDatabase = client[DB_NAME]

# Collection handle
profiles_collection = db["profiles"]
