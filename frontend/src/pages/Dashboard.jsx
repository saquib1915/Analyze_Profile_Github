import { useEffect, useState, useCallback } from "react";
import { Search, RefreshCw, Trash2, GitFork, Star, Eye, BookMarked, MapPin, Building2, Link2, Users, ExternalLink, Clock } from "lucide-react";
import { toast } from "sonner";
import { analyzeUser, fetchHistory, deleteProfile } from "@/lib/api";
import ProfileOverview from "@/components/github/ProfileOverview";
import StatGrid from "@/components/github/StatGrid";
import TopRepos from "@/components/github/TopRepos";
import LanguagesChart from "@/components/github/LanguagesChart";
import HistorySidebar from "@/components/github/HistorySidebar";
import EmptyState from "@/components/github/EmptyState";
import LoadingSkeleton from "@/components/github/LoadingSkeleton";

const EMPTY_BG = "https://static.prod-images.emergentagent.com/jobs/fb321db1-d487-4875-aed3-c133bacc451c/images/dbe43b25f6d4b72d9a68035b8d5e36e6131d99021606f9e0e5b34045c074da82.png";

export default function Dashboard() {
  const [username, setUsername] = useState("");
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const loadHistory = useCallback(async () => {
    try {
      const data = await fetchHistory(15);
      setHistory(data);
    } catch (err) {
      // history is non-critical; log for diagnostics but don't surface to user
      console.error("Failed to load history", err);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleAnalyze = async (uname, force = false) => {
    const target = (uname ?? username).trim();
    if (!target) {
      toast.error("Enter a GitHub username");
      return;
    }
    setLoading(true);
    setProfile(null);
    try {
      const data = await analyzeUser(target, force);
      setProfile(data);
      setUsername(target);
      loadHistory();
      toast.success(data.cached ? `Loaded ${target} from cache` : `Analyzed ${target}`);
    } catch (e) {
      const msg = e?.response?.data?.detail || "Failed to analyze user";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleAnalyze();
  };

  const handleHistoryClick = (uname) => {
    setUsername(uname);
    handleAnalyze(uname, false);
  };

  const handleDelete = async (uname) => {
    try {
      await deleteProfile(uname);
      toast.success(`Removed ${uname} from history`);
      if (profile?.username === uname) setProfile(null);
      loadHistory();
    } catch (e) {
      toast.error("Failed to delete profile");
    }
  };

  return (
    <div className="min-h-screen w-full bg-white" data-testid="dashboard-root">
      {/* Top bar */}
      <header className="border-b border-zinc-200 px-6 py-4 flex items-center justify-between" data-testid="dashboard-header">
        <div className="flex items-baseline gap-3">
          <span className="font-display text-2xl font-black tracking-tighter">GH.ANALYZER</span>
          <span className="font-mono-data text-[10px] uppercase tracking-[0.3em] text-zinc-500">v1 · public api</span>
        </div>
        <span className="font-mono-data text-[10px] uppercase tracking-[0.3em] text-zinc-500 hidden md:inline">
          mysql · cache 1h
        </span>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-[280px_1fr] min-h-[calc(100vh-65px)]">
        {/* Sidebar */}
        <aside className="border-r border-zinc-200 p-6 space-y-8 bg-zinc-50/40" data-testid="sidebar">
          <form onSubmit={handleSubmit} className="space-y-3" data-testid="search-form">
            <label className="block text-xs font-bold uppercase tracking-[0.2em] text-zinc-500">
              Search · username
            </label>
            <div className="flex border border-zinc-300 focus-within:border-[#002FA7] transition-colors">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="torvalds"
                className="flex-1 px-3 py-2.5 font-mono-data text-sm bg-white outline-none placeholder:text-zinc-400"
                data-testid="search-input"
                autoFocus
              />
              <button
                type="submit"
                className="px-3 bg-[#002FA7] text-white hover:bg-[#002080] transition-colors disabled:opacity-50"
                disabled={loading}
                data-testid="search-submit-button"
                aria-label="Analyze user"
              >
                <Search size={16} />
              </button>
            </div>
            <p className="text-[10px] text-zinc-500 leading-relaxed">
              Hits GitHub public API. Data is cached in MySQL for 1 hour.
            </p>
          </form>

          <HistorySidebar
            history={history}
            onSelect={handleHistoryClick}
            onDelete={handleDelete}
            activeUser={profile?.username}
          />
        </aside>

        {/* Main */}
        <main className="p-6 md:p-10" data-testid="main-content">
          {loading && <LoadingSkeleton />}
          {!loading && !profile && <EmptyState bgUrl={EMPTY_BG} />}
          {!loading && profile && (
            <div className="space-y-px bg-zinc-200 gh-fade" data-testid="profile-grid">
              <div className="bg-white">
                <ProfileOverview
                  profile={profile}
                  onRefresh={() => handleAnalyze(profile.username, true)}
                />
              </div>

              <div className="bg-white">
                <StatGrid profile={profile} />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-px bg-zinc-200">
                <div className="bg-white">
                  <TopRepos repos={profile.top_repos || []} />
                </div>
                <div className="bg-white">
                  <LanguagesChart languages={profile.languages || {}} />
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
