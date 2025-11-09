"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Plus, Maximize2 } from "lucide-react";

export default function Agent() {
  const username = "John Doe"; // replace with real username
  const [message, setMessage] = useState("");

  const bubbles = [
    {
      label: "Customer Info",
      color: "bg-cyan-500",
      borderColor: "border-cyan-600",
    },
    {
      label: "Finances",
      color: "bg-emerald-500",
      borderColor: "border-emerald-600",
    },
    {
      label: "Calendar",
      color: "bg-amber-500",
      borderColor: "border-amber-600",
    },
  ];

  return (
    <div className="flex flex-col h-full bg-gray-200 text-gray-100 px-6 py-4">
      {/* HEADER */}
      <h1 className="text-2xl mb-6 text-gray-900">Hello {username}...</h1>

      {/* SCROLLABLE CENTER AREA */}
      <div className="flex-1 overflow-y-auto flex flex-col items-center space-y-6 mb-3">
        {/* PROMPT */}
        <h2 className="text-lg text-gray-900 mb-4">
          What can I help you with today?
        </h2>

        {/* BLOCKS */}
        <div className="flex gap-6">
          {bubbles.map((b) => (
            <div
              key={b.label}
              className="relative w-52 h-40 rounded-2xl bg-gray-900/75 border shadow-md flex flex-col justify-between p-3"
            >
              <span className="text-gray-100 font-medium text-sm">
                {b.label}
              </span>

              <motion.button
                whileHover={{ scale: 1.1 }}
                className={`flex items-center justify-center cursor-pointer w-10 h-10 rounded-lg ${b.color}`}
                title={`Learn more about the ${b.label} category`}
              >
                <Maximize2 className="w-5 h-5 text-gray-900" />
              </motion.button>
              {/* ACCENT BAR */}
              <div
                className={`absolute right-2 h-[80%] w-1.5 rounded-xl ${b.color}`}
              ></div>
            </div>
          ))}
        </div>

        {/* ADDITIONAL TEXT */}
        <div className="max-w-xl text-left text-gray-800 mb-3">
          <p className="mb-2">
            Feel free to{" "}
            <strong>
              click on the category you want to start organizing in
            </strong>{" "}
            or upload your PDF now and I'll determine what category it falls
            into myself!
          </p>
          <p>
            Want to know more about each category?{" "}
            <strong>Click on a card above to learn more!</strong>
          </p>
        </div>
      </div>

      {/* FLOATING BUBBLES */}
      <div className="flex justify-start gap-4 mb-3 cursor-pointer">
        {bubbles.map((b) => (
          <motion.div
            key={b.label}
            whileHover={{ scale: 1.1 }}
            className={`flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium ${b.color} border-2 ${b.borderColor} text-gray-900`}
          >
            {b.label}
          </motion.div>
        ))}
      </div>

      {/* TEXT INPUT */}
      <div className="relative flex items-center bg-gray-900/85 rounded-full px-4 py-2">
        <input
          type="text"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="flex-1 bg-transparent focus:outline-none text-gray-200 placeholder-gray-500"
        />
        <button
          className="flex items-center justify-center w-8 h-8 rounded-full hover:bg-gray-800 transition"
          title="Upload file"
        >
          <Plus className="w-5 h-5 text-gray-300" />
        </button>
      </div>
    </div>
  );
}
