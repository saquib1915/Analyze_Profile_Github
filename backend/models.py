"""SQLAlchemy ORM models for GitHub profile insights."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Profile(Base):
    """Stores a GitHub user's analyzed profile insights.

    Cached for CACHE_TTL_SECONDS. Each fresh analysis updates the row in place
    (UPSERT semantics on `username`).
    """
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(120), unique=True, nullable=False, index=True)

    # Basic profile fields
    name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    html_url = Column(String(500), nullable=True)
    location = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    blog = Column(String(500), nullable=True)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    public_repos = Column(Integer, default=0)
    public_gists = Column(Integer, default=0)
    github_created_at = Column(String(64), nullable=True)

    # Repository aggregate stats (the focus per user request)
    total_stars = Column(Integer, default=0)
    total_forks = Column(Integer, default=0)
    total_watchers = Column(Integer, default=0)
    total_open_issues = Column(Integer, default=0)
    total_repos_analyzed = Column(Integer, default=0)

    # JSON blobs
    top_repos = Column(JSON, nullable=True)   # list of top repo dicts
    languages = Column(JSON, nullable=True)   # {language: repo_count}

    # Caching metadata
    analyzed_at = Column(DateTime, default=utcnow, nullable=False)

    __table_args__ = (
        Index("ix_profiles_analyzed_at", "analyzed_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "html_url": self.html_url,
            "location": self.location,
            "company": self.company,
            "blog": self.blog,
            "followers": self.followers,
            "following": self.following,
            "public_repos": self.public_repos,
            "public_gists": self.public_gists,
            "github_created_at": self.github_created_at,
            "total_stars": self.total_stars,
            "total_forks": self.total_forks,
            "total_watchers": self.total_watchers,
            "total_open_issues": self.total_open_issues,
            "total_repos_analyzed": self.total_repos_analyzed,
            "top_repos": self.top_repos or [],
            "languages": self.languages or {},
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
        }
