"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { User, Mail, Lock, Save, Image, CheckCircle2 } from "lucide-react";

export default function AccountPage() {
  const [formData, setFormData] = useState({
    username: "JohnDoe",
    email: "john@example.com",
    password: "",
    displayName: "John Doe",
  });

  const [isSaved, setIsSaved] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setIsSaved(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Updated account info:", formData);
    setIsSaved(true);
  };

  return (
    <div className="flex flex-col h-full bg-gray-200 text-gray-900 px-8 py-6">
      <h1 className="text-2xl font-semibold mb-6">Account Settings</h1>

      <motion.form
        onSubmit={handleSubmit}
        className="w-full h-[90%] bg-white shadow-md rounded-2xl p-8 border border-gray-300 space-y-6"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {/* PFP */}
        <div className="flex flex-col items-center mb-6">
          <div className="w-24 h-24 bg-gray-300 rounded-full flex items-center justify-center mb-2">
            <Image className="w-8 h-8 text-gray-600" />
          </div>
          <button
            type="button"
            className="text-sm text-indigo-900 hover:underline"
          >
            Change Photo
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* DISPLAY NAME */}
          <div>
            <label className="text-sm font-medium text-gray-700 flex items-center gap-2 mb-1">
              <User className="w-4 h-4" /> Display Name
            </label>
            <input
              type="text"
              name="displayName"
              value={formData.displayName}
              onChange={handleChange}
              className="w-full rounded-lg border border-gray-300 bg-gray-100 p-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* USERNAME */}
          <div>
            <label className="text-sm font-medium text-gray-700 flex items-center gap-2 mb-1">
              <User className="w-4 h-4" /> Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full rounded-lg border border-gray-300 bg-gray-100 p-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* EMAIL */}
          <div>
            <label className="text-sm font-medium text-gray-700 flex items-center gap-2 mb-1">
              <Mail className="w-4 h-4" /> Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full rounded-lg border border-gray-300 bg-gray-100 p-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* PASSWORD */}
          <div>
            <label className="text-sm font-medium text-gray-700 flex items-center gap-2 mb-1">
              <Lock className="w-4 h-4" /> New Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              className="w-full rounded-lg border border-gray-300 bg-gray-100 p-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        {/* SAVE */}
        <div className="flex items-center justify-end pb-2">
          {isSaved && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center text-green-600 text-sm gap-1 mr-auto"
            >
              <CheckCircle2 className="w-4 h-4" />
              Saved!
            </motion.div>
          )}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            className="flex items-center gap-2 bg-gray-900 text-white px-5 py-2 rounded-full shadow-md hover:bg-slate-800 transition"
          >
            <Save className="w-4 h-4" /> Save Changes
          </motion.button>
        </div>
      </motion.form>
    </div>
  );
}
