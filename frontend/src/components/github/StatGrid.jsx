import { Star, GitFork, Eye, BookMarked, CircleDot, BookOpen } from "lucide-react";

const fmt = (n) => new Intl.NumberFormat().format(n ?? 0);

const StatTile = ({ icon: Icon, label, value, testid }) => (
  <div className="p-6 bg-white" data-testid={testid}>
    <div className="flex items-center justify-between mb-3">
      <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">{label}</span>
      <Icon size={16} className="text-[#002FA7]" strokeWidth={1.75} />
    </div>
    <div className="font-display text-4xl font-black tracking-tighter leading-none" data-testid={`${testid}-value`}>
      {fmt(value)}
    </div>
  </div>
);

export default function StatGrid({ profile }) {
  return (
    <section data-testid="stat-grid">
      <div className="px-6 md:px-8 pt-6 pb-2">
        <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-zinc-500">
          // repository aggregate
        </h2>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-zinc-200">
        <StatTile icon={Star} label="Total Stars" value={profile.total_stars} testid="stat-stars" />
        <StatTile icon={GitFork} label="Total Forks" value={profile.total_forks} testid="stat-forks" />
        <StatTile icon={BookMarked} label="Public Repos" value={profile.public_repos} testid="stat-repos" />
        <StatTile icon={CircleDot} label="Open Issues" value={profile.total_open_issues} testid="stat-issues" />
      </div>
      <div className="px-6 md:px-8 py-3 text-[10px] text-zinc-500 border-t border-zinc-200">
        Aggregated across {profile.total_repos_analyzed} owned repositories (excluding forks).
      </div>
    </section>
  );
}
