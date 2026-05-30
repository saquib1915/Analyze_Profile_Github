import { Trash2, History } from "lucide-react";

const formatTime = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
};

export default function HistorySidebar({ history, onSelect, onDelete, activeUser }) {
  return (
    <div data-testid="history-sidebar">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-bold uppercase tracking-[0.2em] text-zinc-500 inline-flex items-center gap-2">
          <History size={12} /> Recent
        </span>
        <span className="text-[10px] text-zinc-400 font-mono-data">{history.length}</span>
      </div>
      {history.length === 0 ? (
        <p className="text-xs text-zinc-400 leading-relaxed">
          No analyzed profiles yet. Search a username to begin.
        </p>
      ) : (
        <ul className="border-t border-zinc-200 divide-y divide-zinc-200">
          {history.map((item) => {
            const active = item.username === activeUser;
            return (
              <li
                key={item.username}
                className={`group flex items-center gap-3 py-2.5 cursor-pointer transition-colors ${
                  active ? "bg-zinc-100" : "hover:bg-zinc-100"
                }`}
                onClick={() => onSelect(item.username)}
                data-testid={`history-item-${item.username}`}
              >
                <img
                  src={item.avatar_url}
                  alt={item.username}
                  className="w-7 h-7 border border-zinc-200 shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-bold truncate" data-testid={`history-username-${item.username}`}>
                    {item.username}
                  </div>
                  <div className="text-[10px] text-zinc-500 truncate">
                    ★ {item.total_stars} · {formatTime(item.analyzed_at)}
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(item.username);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-zinc-400 hover:text-[#FF3333] transition-all p-1"
                  aria-label={`Delete ${item.username}`}
                  data-testid={`history-delete-${item.username}`}
                >
                  <Trash2 size={12} />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
