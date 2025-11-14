"use client";

import { useState, useMemo } from "react";
import Overview from "./overview"; // Import the Overview component. I can resue name because it automatically grabs it out of the folder this file is in

import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";


const tabs = [
  { label: "Overview" , key: "overview" },
  { label: "Transactions", key: "Transactions" },
  { label: "Revenue", key: "Revenue" },
  { label: "Expenses", key: "Expenses" },
  { label: "Banking", key: "Banking" },
  { label: "Finances", key: "Finances" },
  { label: "Taxes", key: "Taxes" },
];

export default function FinancePage() {
  
  const [activeTab, setActiveTab] = useState<string>("overview");
  console.log("Active tab:", activeTab);

   
  return (
    <div className="flex flex-col h-full bg-gray-200 text-gray-900 px-6 py-4">
      {/* Header and tabs */}
      <div className="flex items-center justify-between border-b border-gray-400 pb-3 mb-6">
        <h1 className="text-2xl font-semibold pr-10">Finances</h1>

        {/* Tabs - using the labels and making them into a button */}
        <div className="flex gap-6">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`font-medium text-md transition-colors text-nowrap ${
                activeTab === tab.key
                  ? "text-gray-900 border-b-2 border-gray-900"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Tab content */}
      {activeTab === "overview" && <Overview/>}
      

    </div>
  );
}

