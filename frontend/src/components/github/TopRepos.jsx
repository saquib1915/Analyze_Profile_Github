import { Star, GitFork, ExternalLink } from "lucide-react";

const fmt = (n) => new Intl.NumberFormat().format(n ?? 0);

export default function TopRepos({ repos }) {
  return (
    <section className="p-6 md:p-8" data-testid="top-repos">
      <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-zinc-500 mb-5">
        // top repositories
      </h2>
      {repos.length === 0 ? (
        <p className="text-sm text-zinc-500">No public repositories found.</p>
      ) : (
        <ol className="divide-y divide-zinc-200 border-t border-b border-zinc-200">
          {repos.map((r, i) => (
            <li key={r.full_name || r.name} className="py-4 group" data-testid={`repo-item-${i}`}>
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <a
                    href={r.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-display text-lg font-bold tracking-tight hover:text-[#002FA7] inline-flex items-center gap-1.5"
                    data-testid={`repo-link-${i}`}
                  >
                    {r.name}
                    <ExternalLink size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                  {r.description && (
                    <p className="text-xs text-zinc-600 mt-1 leading-relaxed line-clamp-2">
                      {r.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-4 text-xs text-zinc-600 shrink-0 pt-1">
                  {r.language && (
                    <span className="inline-flex items-center gap-1.5">
                      <span className="w-2 h-2 bg-[#002FA7]" /> {r.language}
                    </span>
                  )}
                  <span className="inline-flex items-center gap-1">
                    <Star size={12} /> {fmt(r.stars)}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <GitFork size={12} /> {fmt(r.forks)}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
