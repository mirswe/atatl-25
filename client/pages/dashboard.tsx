"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Briefcase, Users, DollarSign, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const navigationCards = [
  {
    title: "Agent",
    icon: Briefcase,
    path: "/agent",
    buttonClass: "border-amber-300 text-amber-600 hover:bg-amber-50",
  },
  {
    title: "Customer Info",
    icon: Users,
    path: "/customer",
    buttonClass: "border-cyan-300 text-cyan-600 hover:bg-cyan-50",
  },
  {
    title: "Finances",
    icon: DollarSign,
    path: "/finances",
    buttonClass: "border-emerald-300 text-emerald-600 hover:bg-emerald-50",
  },
];

export default function Dashboard() {
  const router = useRouter();
  const username = "Mr. Doe";

  return (
    <div className="flex flex-col h-full bg-gray-50 px-6 py-4">
      {/* Centered Greeting */}
      <div className="flex-1 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <div className="flex items-center justify-center gap-3">
            <Sparkles className="w-5 h-5 text-orange-500" />
            <h1 className="text-3xl font-medium text-gray-900">
              Hello, {username}
            </h1>
          </div>
        </motion.div>
      </div>

      {/* Navigation Buttons at Bottom */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
        {navigationCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.path}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="w-full sm:w-auto"
            >
              <Button
                variant="outline"
                size="lg"
                className={`w-full sm:w-auto min-w-[180px] ${card.buttonClass}`}
                onClick={() => router.push(card.path)}
              >
                <Icon className="w-5 h-5 mr-2" />
                {card.title}
              </Button>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

