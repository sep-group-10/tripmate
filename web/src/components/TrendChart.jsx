import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

/** Two-series trend chart: a filled area for the primary series and a
 * dashed line for the secondary one, both over a shared x-axis field. */
function TrendChart({ data, xKey, primaryKey, secondaryKey, height = 240 }) {
  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 8, right: 8, left: -24, bottom: 0 }}
        >
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 10, fill: "#9aa0a3" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis hide />
          <Tooltip
            contentStyle={{
              backgroundColor: "#ffffff",
              borderRadius: "10px",
              border: "1px solid #e2e4e5",
              boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
              fontSize: "12px",
            }}
          />
          <Area
            type="monotone"
            dataKey={primaryKey}
            stroke="#e8532b"
            strokeWidth={2.5}
            fill="#fdefeb"
            fillOpacity={0.75}
          />
          <Line
            type="monotone"
            dataKey={secondaryKey}
            stroke="#2f6ff0"
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TrendChart;
