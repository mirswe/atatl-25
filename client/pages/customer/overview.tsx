"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

interface OverviewProps {
  data: { name: string; value: number; color: string }[];
}

export default function Overview({ data }: OverviewProps) {
  const totalCustomers = data.reduce((acc, curr) => acc + curr.value, 0);
  const newThisMonth = 5;
  const activeRatio =
    ((data.find((c) => c.name === "Current")?.value || 0) / totalCustomers) *
    100;

  return (
    <div className="flex flex-col gap-6 md:flex-row">
      {/* DATA (LEFT) */}
      <div className="flex flex-col gap-6 md:w-1/3">
        <div className="bg-gray-900/75 rounded-2xl p-6 shadow-md flex flex-col items-start">
          <span className="text-gray-300 text-sm">Total Customers</span>
          <h3 className="text-white text-2xl font-semibold">
            {totalCustomers}
          </h3>
        </div>
        <div className="bg-gray-900/75 rounded-2xl p-6 shadow-md flex flex-col items-start">
          <span className="text-gray-300 text-sm">
            New Customers This Month
          </span>
          <h3 className="text-white text-2xl font-semibold">{newThisMonth}</h3>
        </div>
        <div className="bg-gray-900/75 rounded-2xl p-6 shadow-md flex flex-col items-start">
          <span className="text-gray-300 text-sm">Active Customer Ratio</span>
          <h3 className="text-white text-2xl font-semibold">
            {activeRatio.toFixed(0)}%
          </h3>
        </div>
      </div>

      {/* PIE CHART (RIGHT) */}
      <div className="bg-gray-900/75 rounded-2xl p-6 shadow-md flex-1 flex flex-col items-center">
        <h2 className="text-white font-semibold text-lg mb-4">
          Customer Distribution
        </h2>
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        {/* Legend */}
        <div className="flex justify-center gap-6 mt-4 flex-wrap">
          {data.map((entry) => (
            <div key={entry.name} className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-white text-sm">{entry.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
