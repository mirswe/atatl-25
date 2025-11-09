"use client";

import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Users,
  Briefcase,
  DollarSign,
  Building2,
  CircleUser,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";

const mainTabs = [
  { name: "Agent", icon: Briefcase, path: "/agent" },
  { name: "Customer", icon: Users, path: "/customer" },
  { name: "Finances", icon: DollarSign, path: "/finances" },
];

const footerTabs = [
  { name: "Account", icon: CircleUser, path: "/account" },
  { name: "Logout", icon: LogOut, path: "/logout" },
];

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();

  const active =
    mainTabs.find((tab) => pathname?.startsWith(tab.path))?.name ||
    footerTabs.find((tab) => pathname?.startsWith(tab.path))?.name ||
    "";

  const mainIndex = mainTabs.findIndex((t) => t.name === active);
  const footerIndex = footerTabs.findIndex((t) => t.name === active);

  const tabHeight = 52;

  const footerOffset = mainTabs.length * tabHeight + 260;

  const sliderTop =
    mainIndex >= 0
      ? mainIndex * tabHeight
      : footerIndex >= 0
      ? footerOffset + footerIndex * tabHeight
      : 0;

  return (
    <aside className="sticky h-full w-64 bg-gray-900 text-gray-300 flex flex-col justify-between">
      {/* TOP SECTION */}
      <div>
        {/* LOGO */}
        <div className="p-4 bg-white flex items-center gap-2">
          <Building2 className="w-6 h-6 text-gray-900" />
          <h1 className="text-xl font-bold text-gray-900">BusinessGo</h1>
        </div>

        {/* MAIN TABS */}
        <nav className="relative flex flex-col mt-6 space-y-2">
          {/* ACTIVE SLIDER */}
          <motion.div
            layout
            className="z-10 absolute right-0 w-1 bg-indigo-500 rounded-full"
            initial={false}
            animate={{ top: sliderTop }}
            transition={{
              type: "spring",
              stiffness: 500,
              damping: 40,
            }}
            style={{ height: 44 }}
          />

          {mainTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = active === tab.name;
            return (
              <button
                key={tab.name}
                onClick={() => router.push(tab.path)}
                className={cn(
                  "cursor-pointer relative flex items-center gap-3 px-5 py-3 text-sm font-medium transition-colors",
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
      </div>

      {/* FOOTER TABS */}
      <div className="relative p-4 border-t border-gray-800 flex flex-col space-y-2">
        {footerTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = active === tab.name;
          return (
            <button
              key={tab.name}
              onClick={() => router.push(tab.path)}
              className={cn(
                "cursor-pointer flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors rounded-md",
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
      </div>
    </aside>
  );
}
