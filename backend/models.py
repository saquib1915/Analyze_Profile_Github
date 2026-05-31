"""Pydantic models for GitHub profile insights stored in MongoDB."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TopRepo(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    html_url: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    updated_at: Optional[str] = None


class Profile(BaseModel):
    """Stored GitHub profile insights (one doc per username, upserted)."""
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str

    # Basic profile fields
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    followers: int = 0
    following: int = 0
    public_repos: int = 0
    public_gists: int = 0
    github_created_at: Optional[str] = None

    # Repository aggregate stats
    total_stars: int = 0
    total_forks: int = 0
    total_watchers: int = 0
    total_open_issues: int = 0
    total_repos_analyzed: int = 0

    # JSON-friendly fields
    top_repos: List[Dict[str, Any]] = Field(default_factory=list)
    languages: Dict[str, int] = Field(default_factory=dict)

    # Caching metadata - stored as ISO string in Mongo for serializability
    analyzed_at: str = Field(default_factory=utcnow_iso)
