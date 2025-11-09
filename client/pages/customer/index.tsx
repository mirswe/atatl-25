"use client";

import { useState, useMemo, useEffect } from "react";
import Overview from "./overview";
import CustomerList from "./customerList";
import { getCustomers, getCustomerStats } from "@/lib/api";
import { Customer, CustomerCategory } from "@/types";

const tabs = [
  { label: "Overview", key: "overview" },
  { label: "Prospective Customers", key: "prospective" },
  { label: "Current Customers", key: "current" },
  { label: "Inactive Customers", key: "inactive" },
];

export default function CustomerPage() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [allCustomers, setAllCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<{
    total: number;
    prospective: number;
    current: number;
    inactive: number;
    uncategorized: number;
  } | null>(null);

  // Fetch customers and stats on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [customersResponse, statsResponse] = await Promise.all([
          getCustomers(),
          getCustomerStats(),
        ]);

        setAllCustomers(customersResponse.customers || []);
        setStats(statsResponse.stats);
      } catch (err) {
        const errorMessage =
          err instanceof Error
            ? err.message
            : typeof err === "string"
            ? err
            : "Failed to load customers";
        setError(errorMessage);
        console.error("Error fetching customers:", err);
        
        // Log more details for debugging
        if (err instanceof Error) {
          console.error("Error stack:", err.stack);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Precompute counts for overview chart
  const customerData = useMemo(() => {
    if (!stats) {
      return [
        { name: "Prospective", value: 0, color: "#8b5cf6" },
        { name: "Current", value: 0, color: "#22c55e" },
        { name: "Inactive", value: 0, color: "#f43f5e" },
      ];
    }

    return [
      { name: "Prospective", value: stats.prospective, color: "#8b5cf6" },
      { name: "Current", value: stats.current, color: "#22c55e" },
      { name: "Inactive", value: stats.inactive, color: "#f43f5e" },
    ];
  }, [stats]);

  // Filter customers for active tab
  const filteredCustomers = useMemo(() => {
    if (activeTab === "prospective")
      return allCustomers.filter(
        (c) => c.category?.toLowerCase() === "prospective"
      );
    if (activeTab === "current")
      return allCustomers.filter(
        (c) => c.category?.toLowerCase() === "current"
      );
    if (activeTab === "inactive")
      return allCustomers.filter(
        (c) => c.category?.toLowerCase() === "inactive"
      );
    return [];
  }, [activeTab, allCustomers]);

  if (loading) {
    return (
      <div className="flex flex-col h-full bg-gray-50 text-gray-900 px-6 py-4">
        <div className="flex items-center justify-center h-full">
          <div className="text-lg text-gray-600">Loading customers...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-full bg-gray-50 text-gray-900 px-6 py-4">
        <div className="flex items-center justify-center h-full">
          <div className="text-lg text-red-600">
            Error loading customers: {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-50 text-gray-900 px-6 py-4">
      {/* Header and tabs */}
      <div className="flex items-center justify-between border-b border-gray-400 pb-3 mb-6">
        <h1 className="text-2xl font-semibold pr-10">Customers</h1>

        {/* Tabs */}
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
      {activeTab === "overview" && (
        <Overview data={customerData} stats={stats} />
      )}
      {activeTab !== "overview" && (
        <CustomerList customers={filteredCustomers} />
      )}
    </div>
  );
}
