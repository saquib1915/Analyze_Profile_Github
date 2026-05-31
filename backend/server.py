from datetime import datetime, timezone
from pathlib import Path
import logging
import os

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import profiles_collection
from github_service import fetch_and_analyze
from models import Profile, utcnow_iso

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "3600"))

app = FastAPI(title="GitHub Profile Analyzer")
api_router = APIRouter(prefix="/api")

logger = logging.getLogger("github-analyzer")
logging.basicConfig(level=logging.INFO)


def _strip_mongo_id(doc: dict) -> dict:
    """Remove MongoDB's internal _id field from a document."""
    if doc and "_id" in doc:
        doc = dict(doc)
        doc.pop("_id", None)
    return doc


def _with_cache_meta(doc: dict) -> dict:
    """Attach cache age / expiry metadata to the response."""
    analyzed_at_str = doc.get("analyzed_at")
    age_seconds = 0
    if analyzed_at_str:
        try:
            analyzed_at = datetime.fromisoformat(analyzed_at_str)
            if analyzed_at.tzinfo is None:
                analyzed_at = analyzed_at.replace(tzinfo=timezone.utc)
            age_seconds = int((datetime.now(timezone.utc) - analyzed_at).total_seconds())
        except ValueError:
            age_seconds = 0
    doc["cache_age_seconds"] = age_seconds
    doc["cache_expires_in_seconds"] = max(0, CACHE_TTL_SECONDS - age_seconds)
    doc["cache_ttl_seconds"] = CACHE_TTL_SECONDS
    return doc


@api_router.get("/")
async def root():
    return {"service": "GitHub Profile Analyzer", "status": "ok"}


@api_router.get("/analyze/{username}")
async def analyze_user(username: str, force: bool = Query(False)):
    """Analyze a GitHub user. Cached for CACHE_TTL_SECONDS in MongoDB."""
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    existing = await profiles_collection.find_one({"username": username})

    if existing and not force:
        existing = _strip_mongo_id(existing)
        analyzed_at_str = existing.get("analyzed_at")
        if analyzed_at_str:
            try:
                analyzed_at = datetime.fromisoformat(analyzed_at_str)
                if analyzed_at.tzinfo is None:
                    analyzed_at = analyzed_at.replace(tzinfo=timezone.utc)
                age = (datetime.now(timezone.utc) - analyzed_at).total_seconds()
                if age < CACHE_TTL_SECONDS:
                    data = _with_cache_meta(existing)
                    data["cached"] = True
                    return data
            except ValueError:
                pass  # treat as stale, fall through to refresh

    # Fetch fresh data from GitHub
    insights = await fetch_and_analyze(username)
    insights["analyzed_at"] = utcnow_iso()

    # Build a validated Profile (preserves existing id if present, else creates one)
    if existing:
        insights["id"] = existing.get("id")
    profile = Profile(**insights)
    doc = profile.model_dump()

    # Upsert by username
    await profiles_collection.update_one(
        {"username": username},
        {"$set": doc},
        upsert=True,
    )

    data = _with_cache_meta(doc)
    data["cached"] = False
    return data


@api_router.get("/profile/{username}")
async def get_profile(username: str):
    """Read a previously analyzed profile from MongoDB (no GitHub call)."""
    doc = await profiles_collection.find_one({"username": username})
    if not doc:
        raise HTTPException(status_code=404, detail="Profile not analyzed yet")
    return _with_cache_meta(_strip_mongo_id(doc))


@api_router.get("/history")
async def get_history(limit: int = Query(10, ge=1, le=50)):
    """List recently analyzed profiles."""
    cursor = profiles_collection.find(
        {},
        {"_id": 0, "username": 1, "name": 1, "avatar_url": 1, "total_stars": 1, "public_repos": 1, "analyzed_at": 1},
    ).sort("analyzed_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


@api_router.delete("/profile/{username}")
async def delete_profile(username: str):
    result = await profiles_collection.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"deleted": username}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def create_indexes():
    """Ensure a unique index on username and a sort index on analyzed_at."""
    await profiles_collection.create_index("username", unique=True)
    await profiles_collection.create_index([("analyzed_at", -1)])
