"use client";

import { motion } from "framer-motion";

interface Customer {
  name: string;
  address: string;
  email: string;
  paymentInfo: string;
  birthday: string;
  gender: string;
  previousOrders: string[];
  previousCorrespondents: string[];
  category: "Prospective" | "Current" | "Inactive";
}

interface CustomerCardProps {
  customer: Customer;
}

export default function CustomerCard({ customer }: CustomerCardProps) {
  const categoryColor =
    customer.category === "Prospective"
      ? "bg-violet-500"
      : customer.category === "Current"
      ? "bg-green-500"
      : "bg-rose-500";

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="relative bg-gray-900/75 rounded-2xl shadow-md p-6 flex flex-col gap-2 w-80"
    >
      {/* ACCENT BAR */}
      <div
        className={`absolute right-0 h-[85%] w-2 rounded-xl ${categoryColor}`}
      ></div>

      {/* Customer Info */}
      <h3 className="text-white font-semibold text-lg">{customer.name}</h3>
      <p className="text-gray-300 text-sm">{customer.address}</p>
      <p className="text-gray-300 text-sm">{customer.email}</p>
      <p className="text-gray-300 text-sm">Payment: {customer.paymentInfo}</p>
      <p className="text-gray-300 text-sm">
        Birthday: {customer.birthday} | Gender: {customer.gender}
      </p>

      {/* Previous Orders */}
      <div className="mt-2">
        <p className="text-gray-400 text-xs font-medium">Previous Orders:</p>
        <ul className="list-disc list-inside text-gray-300 text-sm max-h-20 overflow-y-auto">
          {customer.previousOrders.map((order, idx) => (
            <li key={idx}>{order}</li>
          ))}
        </ul>
      </div>

      {/* Previous Correspondents */}
      <div className="mt-2">
        <p className="text-gray-400 text-xs font-medium">
          Previous Correspondents:
        </p>
        <ul className="list-disc list-inside text-gray-300 text-sm max-h-20 overflow-y-auto">
          {customer.previousCorrespondents.map((person, idx) => (
            <li key={idx}>{person}</li>
          ))}
        </ul>
      </div>
    </motion.div>
  );
}
