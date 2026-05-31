import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const PALETTE = ["#002FA7", "#1F4ABF", "#3D66D7", "#5C81EF", "#7B9DFF", "#9AB9FF", "#B9D5FF", "#D8E0FF"];

// Hoisted to avoid creating new object references on every render
const CHART_MARGIN = { top: 4, right: 16, left: 0, bottom: 4 };
const X_TICK = { fontFamily: "IBM Plex Mono", fontSize: 11, fill: "#52525B" };
const Y_TICK = { fontFamily: "IBM Plex Mono", fontSize: 11, fill: "#09090B" };
const AXIS_LINE = { stroke: "#E4E4E7" };
const TOOLTIP_CURSOR = { fill: "#F4F4F5" };

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-zinc-300 px-3 py-2 font-mono-data text-xs">
      <div className="font-bold">{payload[0].payload.language}</div>
      <div className="text-zinc-600">{payload[0].value} repo{payload[0].value !== 1 ? "s" : ""}</div>
    </div>
  );
};

export default function LanguagesChart({ languages }) {
  const data = Object.entries(languages)
    .map(([language, count]) => ({ language, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  return (
    <section className="p-6 md:p-8 h-full flex flex-col" data-testid="languages-chart">
      <h2 className="font-display text-xs font-bold uppercase tracking-[0.2em] text-zinc-500 mb-5">
        // languages distribution
      </h2>
      {data.length === 0 ? (
        <p className="text-sm text-zinc-500">No language data available.</p>
      ) : (
        <div className="flex-1 min-h-[280px]" data-testid="languages-chart-container">
          <ResponsiveContainer width="100%" height={Math.max(280, data.length * 36)}>
            <BarChart data={data} layout="vertical" margin={CHART_MARGIN}>
              <XAxis
                type="number"
                tick={X_TICK}
                axisLine={AXIS_LINE}
                tickLine={false}
                allowDecimals={false}
              />
              <YAxis
                type="category"
                dataKey="language"
                tick={Y_TICK}
                axisLine={AXIS_LINE}
                tickLine={false}
                width={90}
              />
              <Tooltip content={<CustomTooltip />} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="count" radius={0}>
                {data.map((d) => (
                  <Cell key={d.language} fill={PALETTE[data.indexOf(d) % PALETTE.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}
