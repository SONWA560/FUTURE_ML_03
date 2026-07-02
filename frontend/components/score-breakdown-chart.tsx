"use client";

import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, XAxis, YAxis } from "recharts";

interface ScoreBreakdownChartProps {
  skillScore: number;
  similarityScore: number;
}

export function ScoreBreakdownChart({ skillScore, similarityScore }: ScoreBreakdownChartProps) {
  const data = [
    { name: "Skill match", value: Math.round(skillScore * 100) },
    { name: "Text similarity", value: Math.round(similarityScore * 100) },
  ];

  return (
    <div className="h-40 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24, top: 8, bottom: 8 }}>
          <CartesianGrid horizontal={false} strokeDasharray="3 3" className="stroke-border" />
          <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} hide />
          <YAxis type="category" dataKey="name" width={100} tickLine={false} axisLine={false} />
          <Bar dataKey="value" fill="var(--chart-1)" radius={[0, 4, 4, 0]} barSize={28}>
            <LabelList
              dataKey="value"
              position="right"
              formatter={(v: unknown) => `${v}%`}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
