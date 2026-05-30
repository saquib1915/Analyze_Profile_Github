export default function LoadingSkeleton() {
  return (
    <div className="space-y-px bg-zinc-200" data-testid="loading-skeleton">
      <div className="bg-white p-8 flex gap-6">
        <div className="w-28 h-28 gh-skeleton" />
        <div className="flex-1 space-y-3">
          <div className="h-8 w-2/3 gh-skeleton" />
          <div className="h-3 w-1/3 gh-skeleton" />
          <div className="h-3 w-4/5 gh-skeleton" />
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-zinc-200">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="bg-white p-6 space-y-3">
            <div className="h-3 w-1/2 gh-skeleton" />
            <div className="h-10 w-2/3 gh-skeleton" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-px bg-zinc-200">
        <div className="bg-white p-8 space-y-4">
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} className="h-12 gh-skeleton" />
          ))}
        </div>
        <div className="bg-white p-8 space-y-3">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-6 gh-skeleton" />
          ))}
        </div>
      </div>
    </div>
  );
}
