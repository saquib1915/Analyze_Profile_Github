from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone, timedelta
from pathlib import Path
import os
import logging

from database import engine, Base, get_db
from models import Profile, utcnow
from github_service import fetch_and_analyze

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

CACHE_TTL_SECONDS = int(os.environ.get("CACHE_TTL_SECONDS", "3600"))

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GitHub Profile Analyzer")
api_router = APIRouter(prefix="/api")

logger = logging.getLogger("github-analyzer")
logging.basicConfig(level=logging.INFO)


def _profile_with_cache_meta(p: Profile) -> dict:
    data = p.to_dict()
    # Compute cache freshness
    analyzed_at = p.analyzed_at
    if analyzed_at and analyzed_at.tzinfo is None:
        analyzed_at = analyzed_at.replace(tzinfo=timezone.utc)
    age_seconds = (datetime.now(timezone.utc) - analyzed_at).total_seconds() if analyzed_at else None
    expires_in = max(0, CACHE_TTL_SECONDS - int(age_seconds)) if age_seconds is not None else 0
    data["cache_age_seconds"] = int(age_seconds) if age_seconds is not None else 0
    data["cache_expires_in_seconds"] = expires_in
    data["cache_ttl_seconds"] = CACHE_TTL_SECONDS
    return data


@api_router.get("/")
def root():
    return {"service": "GitHub Profile Analyzer", "status": "ok"}


@api_router.get("/analyze/{username}")
async def analyze_user(
    username: str,
    force: bool = Query(False, description="Bypass cache and re-fetch from GitHub"),
    db: Session = Depends(get_db),
):
    """Analyze a GitHub user.

    Returns cached data if a fresh entry (<= CACHE_TTL_SECONDS) exists,
    otherwise calls the GitHub API, persists insights to MySQL, and returns them.
    """
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    existing = db.query(Profile).filter(Profile.username == username).first()

    if existing and not force:
        analyzed_at = existing.analyzed_at
        if analyzed_at and analyzed_at.tzinfo is None:
            analyzed_at = analyzed_at.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - analyzed_at).total_seconds()
        if age < CACHE_TTL_SECONDS:
            data = _profile_with_cache_meta(existing)
            data["cached"] = True
            return data

    # Fetch fresh data
    insights = await fetch_and_analyze(username)

    if existing:
        for k, v in insights.items():
            setattr(existing, k, v)
        existing.analyzed_at = utcnow()
        profile = existing
    else:
        profile = Profile(**insights)
        profile.analyzed_at = utcnow()
        db.add(profile)

    db.commit()
    db.refresh(profile)

    data = _profile_with_cache_meta(profile)
    data["cached"] = False
    return data


@api_router.get("/profile/{username}")
def get_profile(username: str, db: Session = Depends(get_db)):
    """Get a previously analyzed profile from the database (no GitHub call)."""
    profile = db.query(Profile).filter(Profile.username == username).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not analyzed yet")
    return _profile_with_cache_meta(profile)


@api_router.get("/history")
def get_history(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """List recently analyzed profiles."""
    profiles = (
        db.query(Profile)
        .order_by(desc(Profile.analyzed_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "username": p.username,
            "name": p.name,
            "avatar_url": p.avatar_url,
            "total_stars": p.total_stars,
            "public_repos": p.public_repos,
            "analyzed_at": p.analyzed_at.isoformat() if p.analyzed_at else None,
        }
        for p in profiles
    ]


@api_router.delete("/profile/{username}")
def delete_profile(username: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.username == username).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    return {"deleted": username}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
