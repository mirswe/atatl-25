"use client";
//imports needed for recharts
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

//props interface
interface OverviewProps {
  data: { name: string; value: number; color: string }[];
}

//placeholder data for pie chart
const data = [
  { name: "Operational", value: 200, color: "#0088FE" },
  { name: "Employee & Labor", value: 300, color: "#00C49F" },
  { name: "Marketing", value: 100, color: "#FFBB28" },
  { name: "Inventory", value: 400, color: "#FF8042" },
];

//colors for pie chart segments
const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

export default function Overview() {

  return (
    <div className="flex flex-row gap-6">
      
      {/* DATA (LEFT) */}
      <main className="flex flex-col items-center w-full max-w-2xl gap-6">
        <h2 className="text-2xl font-semibold text-blue">Recent Transactions</h2>
        <table className="min-w-full border border-gray-300 rounded-lg overflow-hidden">
          <thead className="bg-gray-200 dark:bg-zinc-800">
            <tr>
              <th className="px-4 py-2 text-left text-gray-700 dark:text-gray-200">Date</th>
              <th className="px-4 py-2 text-left text-gray-700 dark:text-gray-200">Merchant</th>
              <th className="px-4 py-2 text-left text-gray-700 dark:text-gray-200 text-center">Amount (USD)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-zinc-700">
            <tr>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">11/10/25</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">U.S. Foods</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">-2868.15</td>
            </tr>
            <tr>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">11/10/25</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">Uber</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">-57.80</td>
            </tr>
            <tr>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">11/10/25</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">Georgia Power</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">-754.90</td>
            </tr>
            <tr>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">11/09/25</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">Doordash</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">-79.34</td>
            </tr>
            <tr>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">11/09/25</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">Rent</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">-2840.00</td>
            </tr>
            <tr>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">11/08/25</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">InstaCart</td>
              <td className="px-4 py-2 text-gray-800 dark:text-gray-100">-46.93</td>
            </tr>
          </tbody>
        </table>
      </main>

      {/* PIE CHART (RIGHT) */}
            <div className="bg-gray-900/75 rounded-2xl p-6 shadow-md flex-1 flex flex-col items-center">
              <h2 className="text-white font-semibold text-sm mb-4">
                Expense Distribution
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
                      labelLine={false} // remove lines
                      label={({ name, index }) => (
                        <text style={{ fontSize: 2 }} fill={COLORS[index % COLORS.length]} textAnchor="middle">
                          {name}
                        </text>
                      )}
                    >
                      {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
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
                style={{ backgroundColor: entry.color}}
              />
              <span className="text-white text-sm">{entry.name}</span>
            </div>
          ))}
        </div>
            </div>

    </div>
    

    

    



  );
}
