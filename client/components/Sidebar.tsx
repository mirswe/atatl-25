"use client";

import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  DollarSign,
  Building2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const tabs = [
  { name: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
  { name: "Agent", icon: Briefcase, path: "/agent" },
  { name: "Customer", icon: Users, path: "/customer" },
  { name: "Finances", icon: DollarSign, path: "/finances" },
];

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();

  // Determine active tab based on current path
  const active =
    tabs.find((tab) => pathname?.startsWith(tab.path))?.name || "Dashboard";

  return (
    <aside className="sticky h-full w-64 bg-gray-900 text-gray-300 flex flex-col">
      {/* LOGO */}
      <div className="p-4 bg-white flex items-center gap-2">
        <Building2 className="w-6 h-6 text-gray-900" />
        <h1 className="text-xl font-bold text-gray-900">BusinessGo</h1>
      </div>

      {/* TAB SECTION */}
      <nav className="relative flex-1 flex flex-col mt-6 space-y-2">
        {/* ACTIVE SLIDER */}
        <motion.div
          layout
          className="z-10 absolute right-0 w-1 bg-indigo-500 rounded-full"
          initial={false}
          animate={{
            top: tabs.findIndex((t) => t.name === active) * 52,
          }}
          transition={{
            type: "spring",
            stiffness: 500,
            damping: 40,
          }}
          style={{ height: 44 }}
        />

        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = active === tab.name;
          return (
            <button
              key={tab.name}
              onClick={() => router.push(tab.path)}
              className={cn(
                "relative flex items-center gap-3 px-5 py-3 text-sm font-medium transition-colors",
                isActive
                  ? "text-white bg-gray-800"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/40"
              )}
            >
              <Icon className="w-5 h-5" />
              {tab.name}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
