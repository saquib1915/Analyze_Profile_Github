import { MapPin, Building2, Link2, Users, RefreshCw, ExternalLink, Clock } from "lucide-react";

const fmt = (n) => new Intl.NumberFormat().format(n ?? 0);

const CacheBadge = ({ cached, age, ttl }) => {
  const minutesAgo = Math.floor((age || 0) / 60);
  return (
    <span
      className={`inline-flex items-center gap-1.5 border px-2 py-1 text-[10px] uppercase tracking-[0.2em] ${
        cached ? "border-[#002FA7] text-[#002FA7]" : "border-zinc-400 text-zinc-600"
      }`}
      data-testid="cache-badge"
      title={`TTL ${ttl}s`}
    >
      <Clock size={11} />
      {cached ? `cached · ${minutesAgo}m ago` : "fresh"}
    </span>
  );
};

export default function ProfileOverview({ profile, onRefresh }) {
  return (
    <section className="p-6 md:p-8" data-testid="profile-overview">
      <div className="flex flex-col md:flex-row gap-6 md:items-start">
        <img
          src={profile.avatar_url}
          alt={profile.username}
          className="w-24 h-24 md:w-28 md:h-28 border border-zinc-200 grayscale hover:grayscale-0 transition-all"
          data-testid="profile-avatar"
        />
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-3 mb-2">
            <h1 className="font-display text-3xl md:text-4xl font-black tracking-tighter leading-none" data-testid="profile-name">
              {profile.name || profile.username}
            </h1>
            <a
              href={profile.html_url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono-data text-sm text-[#002FA7] hover:underline inline-flex items-center gap-1"
              data-testid="profile-github-link"
            >
              @{profile.username} <ExternalLink size={12} />
            </a>
          </div>

          {profile.bio && (
            <p className="text-sm text-zinc-700 max-w-2xl mb-4 leading-relaxed" data-testid="profile-bio">
              {profile.bio}
            </p>
          )}

          <ul className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-zinc-600">
            {profile.location && (
              <li className="inline-flex items-center gap-1.5" data-testid="profile-location">
                <MapPin size={13} /> {profile.location}
              </li>
            )}
            {profile.company && (
              <li className="inline-flex items-center gap-1.5" data-testid="profile-company">
                <Building2 size={13} /> {profile.company}
              </li>
            )}
            {profile.blog && (
              <li className="inline-flex items-center gap-1.5" data-testid="profile-blog">
                <Link2 size={13} />
                <a
                  href={profile.blog.startsWith("http") ? profile.blog : `https://${profile.blog}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-[#002FA7] hover:underline"
                >
                  {profile.blog}
                </a>
              </li>
            )}
            <li className="inline-flex items-center gap-1.5" data-testid="profile-followers">
              <Users size={13} /> <b>{fmt(profile.followers)}</b> followers · <b>{fmt(profile.following)}</b> following
            </li>
          </ul>
        </div>

        <div className="flex flex-col items-start md:items-end gap-3">
          <CacheBadge
            cached={profile.cached}
            age={profile.cache_age_seconds}
            ttl={profile.cache_ttl_seconds}
          />
          <button
            onClick={onRefresh}
            className="inline-flex items-center gap-2 border border-zinc-300 px-3 py-1.5 text-xs uppercase tracking-[0.2em] hover:bg-zinc-100 transition-colors"
            data-testid="refresh-button"
          >
            <RefreshCw size={12} /> Refresh
          </button>
        </div>
      </div>
    </section>
  );
}
