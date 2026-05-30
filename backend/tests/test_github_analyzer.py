"""Backend tests for GitHub Profile Analyzer."""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://gh-insights-api.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------- Health ----------
def test_health(client):
    r = client.get(f"{API}/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert "service" in data


# ---------- Analyze flow ----------
def test_analyze_octocat_fresh(client):
    # Ensure clean state
    client.delete(f"{API}/profile/octocat")
    r = client.get(f"{API}/analyze/octocat", timeout=60)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["username"] == "octocat"
    assert data["cached"] is False
    assert "avatar_url" in data and data["avatar_url"]
    for k in ["followers", "following", "public_repos", "total_stars",
              "total_forks", "total_watchers", "total_open_issues",
              "total_repos_analyzed"]:
        assert k in data, f"missing {k}"
        assert isinstance(data[k], int)
    assert isinstance(data["top_repos"], list)
    assert len(data["top_repos"]) <= 5
    assert isinstance(data["languages"], dict)
    assert data["cache_ttl_seconds"] == 3600


def test_analyze_octocat_cached(client):
    r1 = client.get(f"{API}/analyze/octocat")
    assert r1.status_code == 200
    analyzed_at_1 = r1.json()["analyzed_at"]

    r2 = client.get(f"{API}/analyze/octocat")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["cached"] is True
    assert data2["analyzed_at"] == analyzed_at_1


def test_force_refresh(client):
    # Ensure something cached first
    client.get(f"{API}/analyze/octocat")
    r1 = client.get(f"{API}/analyze/octocat")
    first_analyzed = r1.json()["analyzed_at"]
    time.sleep(1.1)
    r2 = client.get(f"{API}/analyze/octocat", params={"force": "true"}, timeout=60)
    assert r2.status_code == 200, r2.text
    data2 = r2.json()
    assert data2["cached"] is False
    assert data2["analyzed_at"] != first_analyzed


def test_analyze_nonexistent_user(client):
    r = client.get(f"{API}/analyze/nonexistentuser12345xyz", timeout=60)
    assert r.status_code == 404
    body = r.json()
    assert "detail" in body


# ---------- Persistence: profile & history ----------
def test_get_stored_profile(client):
    # Make sure octocat is analyzed
    client.get(f"{API}/analyze/octocat")
    r = client.get(f"{API}/profile/octocat")
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "octocat"
    # No cached field on this endpoint, but core data present
    assert "total_stars" in data


def test_get_profile_404(client):
    # Make sure not present
    client.delete(f"{API}/profile/TEST_neveranalyzeduser_zzz")
    r = client.get(f"{API}/profile/TEST_neveranalyzeduser_zzz")
    assert r.status_code == 404


def test_history_returns_octocat(client):
    client.get(f"{API}/analyze/octocat")
    r = client.get(f"{API}/history", params={"limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    usernames = [i["username"] for i in items]
    assert "octocat" in usernames
    # Required fields
    for i in items:
        assert "analyzed_at" in i
        assert "total_stars" in i
        assert "avatar_url" in i


def test_history_ordered_desc(client):
    # Force refresh octocat to make it newest
    client.get(f"{API}/analyze/octocat", params={"force": "true"}, timeout=60)
    r = client.get(f"{API}/history", params={"limit": 10})
    items = r.json()
    if len(items) >= 2:
        # Ensure descending order by analyzed_at
        timestamps = [i["analyzed_at"] for i in items]
        assert timestamps == sorted(timestamps, reverse=True)
    assert items[0]["username"] == "octocat"


# ---------- Delete ----------
def test_delete_profile(client):
    # Ensure exists
    client.get(f"{API}/analyze/octocat")
    r = client.delete(f"{API}/profile/octocat")
    assert r.status_code == 200
    assert r.json().get("deleted") == "octocat"
    # Verify removed
    r2 = client.get(f"{API}/profile/octocat")
    assert r2.status_code == 404


def test_delete_nonexistent(client):
    r = client.delete(f"{API}/profile/TEST_doesnotexist_abc")
    assert r.status_code == 404
