"""GitHub public API client + analyzer.

Uses unauthenticated public API endpoints. Aggregates repository stats
into a single insights payload that gets persisted in MySQL.
"""
import os
import httpx
from collections import Counter
from fastapi import HTTPException

GITHUB_API_BASE = os.environ.get("GITHUB_API_BASE", "https://api.github.com")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-profile-analyzer",
}


async def _get(client: httpx.AsyncClient, path: str, params: dict | None = None):
    url = f"{GITHUB_API_BASE}{path}"
    resp = await client.get(url, params=params, headers=HEADERS, timeout=20.0)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="GitHub user not found")
    if resp.status_code == 403:
        # Rate limited
        raise HTTPException(
            status_code=429,
            detail="GitHub API rate limit exceeded. Please try again later.",
        )
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error: {resp.status_code}",
        )
    return resp.json()


async def fetch_and_analyze(username: str) -> dict:
    """Fetch user + repos from GitHub, aggregate insights."""
    async with httpx.AsyncClient() as client:
        user = await _get(client, f"/users/{username}")

        # Fetch up to 100 most recently updated public repos.
        repos = await _get(
            client,
            f"/users/{username}/repos",
            params={"per_page": 100, "sort": "updated", "type": "owner"},
        )

    # Filter out forks for "owned" stats - keep both views
    own_repos = [r for r in repos if not r.get("fork")]

    total_stars = sum(r.get("stargazers_count", 0) for r in own_repos)
    total_forks = sum(r.get("forks_count", 0) for r in own_repos)
    total_watchers = sum(r.get("watchers_count", 0) for r in own_repos)
    total_open_issues = sum(r.get("open_issues_count", 0) for r in own_repos)

    # Languages distribution (by repo count primary language)
    lang_counter = Counter()
    for r in own_repos:
        lang = r.get("language")
        if lang:
            lang_counter[lang] += 1
    languages = dict(lang_counter.most_common(10))

    # Top 5 repos by stars
    top_repos_sorted = sorted(
        own_repos, key=lambda r: r.get("stargazers_count", 0), reverse=True
    )[:5]
    top_repos = [
        {
            "name": r.get("name"),
            "full_name": r.get("full_name"),
            "description": r.get("description"),
            "html_url": r.get("html_url"),
            "language": r.get("language"),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "watchers": r.get("watchers_count", 0),
            "open_issues": r.get("open_issues_count", 0),
            "updated_at": r.get("updated_at"),
        }
        for r in top_repos_sorted
    ]

    return {
        "username": user.get("login"),
        "name": user.get("name"),
        "bio": user.get("bio"),
        "avatar_url": user.get("avatar_url"),
        "html_url": user.get("html_url"),
        "location": user.get("location"),
        "company": user.get("company"),
        "blog": user.get("blog"),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "public_repos": user.get("public_repos", 0),
        "public_gists": user.get("public_gists", 0),
        "github_created_at": user.get("created_at"),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_watchers": total_watchers,
        "total_open_issues": total_open_issues,
        "total_repos_analyzed": len(own_repos),
        "top_repos": top_repos,
        "languages": languages,
    }
