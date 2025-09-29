"use client";

import { LineChart, Line, ResponsiveContainer } from 'recharts';

interface Props {
  data: number[];
  stroke?: string;
}

export default function Sparkline({ data, stroke = '#10B981' }: Props) {
  const chartData = (data || []).map((v, i) => ({ i, v }));
  return (
    <div style={{ width: '100%', height: 40 }}>
      <ResponsiveContainer>
        <LineChart data={chartData} margin={{ top: 8, bottom: 0, left: 0, right: 0 }}>
          <Line type="monotone" dataKey="v" stroke={stroke} dot={false} strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}




