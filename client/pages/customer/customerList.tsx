"use client";

import CustomerCard from "./customerCard";
import { Customer } from "@/types";

interface CustomerListProps {
  customers: Customer[];
}

export default function CustomerList({ customers }: CustomerListProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
      {customers.map((c) => (
        <CustomerCard key={c.email} customer={c} />
      ))}
    </div>
  );
}
