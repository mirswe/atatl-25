"use client";

import { useState, useMemo } from "react";
import Overview from "./overview";
import CustomerList from "./customerList";
import CustomerCard from "./customerCard";

// placeholder data
const allCustomers = [
  {
    name: "Alice Johnson",
    email: "alice@example.com",
    category: "Prospective",
    address: "123 Main St",
    paymentInfo: "Visa ****1234",
    birthday: "1990-02-14",
    gender: "Female",
    previousOrders: ["Order #1001", "Order #1005"],
    previousCorrespondents: ["Bob Smith", "Carol Lee"],
  },
  {
    name: "Bob Smith",
    email: "bob@example.com",
    category: "Current",
    address: "456 Oak Ave",
    paymentInfo: "Mastercard ****5678",
    birthday: "1985-08-23",
    gender: "Male",
    previousOrders: ["Order #1002"],
    previousCorrespondents: ["Alice Johnson"],
  },
  {
    name: "Charlie Davis",
    email: "charlie@example.com",
    category: "Inactive",
    address: "789 Pine Rd",
    paymentInfo: "Paypal",
    birthday: "1978-12-05",
    gender: "Male",
    previousOrders: [],
    previousCorrespondents: [],
  },
  {
    name: "Diana Lee",
    email: "diana@example.com",
    category: "Current",
    address: "321 Cedar St",
    paymentInfo: "Visa ****9876",
    birthday: "1992-05-19",
    gender: "Female",
    previousOrders: ["Order #1010", "Order #1011"],
    previousCorrespondents: ["Bob Smith"],
  },
  {
    name: "Evan White",
    email: "evan@example.com",
    category: "Prospective",
    address: "654 Maple Blvd",
    paymentInfo: "Mastercard ****4321",
    birthday: "1988-11-12",
    gender: "Male",
    previousOrders: [],
    previousCorrespondents: [],
  },
];

const tabs = [
  { label: "Overview", key: "overview" },
  { label: "Prospective Customers", key: "prospective" },
  { label: "Current Customers", key: "current" },
  { label: "Inactive Customers", key: "inactive" },
];

export default function CustomerPage() {
  const [activeTab, setActiveTab] = useState<string>("overview");

  // Precompute counts for overview chart
  const customerData = useMemo(() => {
    const counts = {
      Prospective: 0,
      Current: 0,
      Inactive: 0,
    };
    allCustomers.forEach((c) => {
      counts[c.category] = (counts[c.category] || 0) + 1;
    });
    return [
      { name: "Prospective", value: counts.Prospective, color: "#8b5cf6" },
      { name: "Current", value: counts.Current, color: "#22c55e" },
      { name: "Inactive", value: counts.Inactive, color: "#f43f5e" },
    ];
  }, []);

  // Filter customers for active tab
  const filteredCustomers = useMemo(() => {
    if (activeTab === "prospective")
      return allCustomers.filter((c) => c.category === "Prospective");
    if (activeTab === "current")
      return allCustomers.filter((c) => c.category === "Current");
    if (activeTab === "inactive")
      return allCustomers.filter((c) => c.category === "Inactive");
    return [];
  }, [activeTab]);

  return (
    <div className="flex flex-col h-full bg-gray-200 text-gray-900 px-6 py-4">
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
      {activeTab === "overview" && <Overview data={customerData} />}
      {activeTab !== "overview" && (
        <CustomerList customers={filteredCustomers} />
      )}
    </div>
  );
}
/**Type '{ name: string; email: string; category: string; address: string; paymentInfo: string; birthday: string; gender: string; previousOrders: string[]; previousCorrespondents: string[]; }[]' is not assignable to type 'Customer[]'.
  Type '{ name: string; email: string; category: string; address: string; paymentInfo: string; birthday: string; gender: string; previousOrders: string[]; previousCorrespondents: string[]; }' is not assignable to type 'Customer'.
    Types of property 'category' are incompatible.
      Type 'string' is not assignable to type '"Prospective" | "Current" | "Inactive"'.ts(2322)
customerList.tsx(18, 3): The expected type comes from property 'customers' which is declared here on type 'IntrinsicAttributes & CustomerListProps' */
