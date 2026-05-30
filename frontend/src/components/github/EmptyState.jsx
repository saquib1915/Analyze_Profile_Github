import { ArrowLeft, Github } from "lucide-react";

export default function EmptyState({ bgUrl }) {
  return (
    <div
      className="relative border border-zinc-200 min-h-[60vh] flex items-center justify-center overflow-hidden"
      data-testid="empty-state"
    >
      {bgUrl && (
        <img
          src={bgUrl}
          alt=""
          className="absolute inset-0 w-full h-full object-cover opacity-10 grayscale pointer-events-none"
        />
      )}
      <div className="relative z-10 max-w-md text-center px-6">
        <Github size={36} strokeWidth={1.5} className="mx-auto mb-6 text-[#002FA7]" />
        <h2 className="font-display text-3xl md:text-4xl font-black tracking-tighter leading-none mb-3">
          Analyze any
          <br />
          GitHub profile.
        </h2>
        <p className="text-sm text-zinc-600 leading-relaxed mb-8">
          Type a GitHub username on the left to compute aggregate repository
          insights — stars, forks, top repos, and language distribution.
          Cached for one hour.
        </p>
        <div className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-zinc-500">
          <ArrowLeft size={12} /> start with a username
        </div>
      </div>
    </div>
  );
}
