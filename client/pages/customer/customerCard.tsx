"use client";

import { motion } from "framer-motion";
import { Customer } from "@/types";

interface CustomerCardProps {
  customer: Customer;
}

export default function CustomerCard({ customer }: CustomerCardProps) {
  const categoryColor =
    customer.category === "Prospective"
      ? "bg-violet-500"
      : customer.category === "Current"
      ? "bg-green-500"
      : customer.category === "Inactive"
      ? "bg-rose-500"
      : "bg-gray-500";

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
      <h3 className="text-white font-semibold text-lg">
        {customer.name || "Unknown Customer"}
      </h3>
      {customer.address && (
        <p className="text-gray-300 text-sm">{customer.address}</p>
      )}
      {customer.email && <p className="text-gray-300 text-sm">{customer.email}</p>}
      {customer.paymentMethod && (
        <p className="text-gray-300 text-sm">
          Payment: {customer.paymentMethod}
          {customer.paymentLast4 && ` ****${customer.paymentLast4}`}
        </p>
      )}
      {customer.birthday && (
        <p className="text-gray-300 text-sm">Birthday: {customer.birthday}</p>
      )}

      {/* Previous Orders */}
      {customer.prevOrders && customer.prevOrders.length > 0 && (
        <div className="mt-2">
          <p className="text-gray-400 text-xs font-medium">Previous Orders:</p>
          <ul className="list-disc list-inside text-gray-300 text-sm max-h-20 overflow-y-auto">
            {customer.prevOrders.map((order, idx) => (
              <li key={idx}>
                {order.order_number || order.order_id || `Order #${idx + 1}`}
                {order.date && ` - ${order.date}`}
                {order.amount && ` - $${order.amount}`}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Interests */}
      {customer.interests && customer.interests.length > 0 && (
        <div className="mt-2">
          <p className="text-gray-400 text-xs font-medium">Interests:</p>
          <ul className="list-disc list-inside text-gray-300 text-sm max-h-20 overflow-y-auto">
            {customer.interests.map((interest, idx) => (
              <li key={idx}>{interest}</li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}
