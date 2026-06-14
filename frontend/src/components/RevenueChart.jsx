import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function RevenueChart({ title, data, color }) {
  return (
    <div className="chart-card">
      <div className="chart-head">
        <h3>{title}</h3>
        <span>{data.length ? `${data.length} records` : "No payments"}</span>
      </div>
      <div className="chart-box">
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id={title} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.8} />
                <stop offset="95%" stopColor={color} stopOpacity={0.08} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#ffffff44" />
            <XAxis dataKey="label" tick={{ fill: "#fff", fontSize: 11 }} />
            <YAxis tick={{ fill: "#fff", fontSize: 11 }} />
            <Tooltip />
            <Area type="monotone" dataKey="revenue" stroke={color} fill={`url(#${title})`} strokeWidth={3} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default RevenueChart;
