# GitHub Profile Analyzer — PRD

## Original Problem Statement
> Build a backend service that analyzes a GitHub user profile using the GitHub public API and stores useful insights in a MySQL database.

## User Choices (clarified Feb 2026)
- **Database**: MySQL (we use MariaDB 10.11, MySQL-compatible)
- **Insights focus**: Repository stats
- **GitHub auth**: Unauthenticated public API (60 req/hour limit, mitigated by cache)
- **Frontend**: Yes, simple UI to view analyzed profiles
- **Caching**: 1-hour TTL

## Architecture
- **Backend**: FastAPI + SQLAlchemy ORM + PyMySQL → MariaDB on `127.0.0.1:3306` (db `github_analyzer`)
- **Frontend**: React 19 + Tailwind + shadcn primitives + Recharts (Chivo / IBM Plex Mono fonts)
- **GitHub client**: `httpx` against `https://api.github.com`
- **MySQL supervisor entry**: `/etc/supervisor/conf.d/mariadb.conf`

## API Endpoints (all under `/api`)
- `GET /` — health
- `GET /analyze/{username}?force=bool` — fetch + analyze + persist; cached for 1h
- `GET /profile/{username}` — read cached row from MySQL
- `GET /history?limit=N` — recently analyzed profiles
- `DELETE /profile/{username}` — purge a cached row

## Data Model — `profiles` table
Username (unique), name, bio, avatar_url, location, company, blog, followers, following, public_repos, public_gists, github_created_at, total_stars, total_forks, total_watchers, total_open_issues, total_repos_analyzed, top_repos (JSON), languages (JSON), analyzed_at.

## What's Been Implemented (Feb 2026)
- ✅ MySQL/MariaDB installed + supervised, schema auto-created
- ✅ GitHub public API client with rate-limit / 404 handling
- ✅ Repo aggregate computation (stars, forks, watchers, open issues), top-5 repos, languages distribution
- ✅ 1-hour cache with force-refresh support
- ✅ History endpoint + DELETE
- ✅ Dashboard UI: search, profile overview, 4 stat tiles, top repos, languages bar chart, history sidebar, cache badge, empty state, loading skeleton, toasts
- ✅ Full backend pytest suite (11/11) and frontend Playwright E2E (100%)

## Backlog / Next Action Items
- **P1**: Paginate `/users/{u}/repos` to handle users with >100 repos
- **P1**: Add optional GitHub PAT in `.env` to raise rate limit to 5000/hr
- **P2**: Languages distribution weighted by repo size (bytes) instead of repo count via `/languages` endpoint
- **P2**: Compare two GitHub profiles side-by-side
- **P2**: Export profile report as JSON/PDF
- **P3**: Activity / contribution timeline (events API)

## User Personas
- Developers vetting candidates or peers
- OSS maintainers benchmarking their own profile
- Recruiters doing quick technical scans

## Files of Interest
- Backend: `/app/backend/{server.py, github_service.py, models.py, database.py}`
- Frontend: `/app/frontend/src/pages/Dashboard.jsx`, `/app/frontend/src/components/github/*`
- Tests: `/app/backend/tests/test_github_analyzer.py`
