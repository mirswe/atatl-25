"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Plus, Maximize2, Send, Loader2 } from "lucide-react";
import {
  chatWithAgent,
  chatWithCustomerAgent,
  chatWithFinanceAgent,
} from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function Agent() {
  const username = "John Doe"; // replace with real username
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<"general" | "customer" | "finance" | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  // Load session from localStorage on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem("agent_session_id");
    if (savedSessionId) {
      setSessionId(savedSessionId);
    }
  }, []);

  // Save session to localStorage when it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem("agent_session_id", sessionId);
    }
  }, [sessionId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const bubbles = [
    {
      label: "Customer Info",
      color: "bg-cyan-500",
      borderColor: "border-cyan-600",
      agent: "customer" as const,
    },
    {
      label: "Finances",
      color: "bg-emerald-500",
      borderColor: "border-emerald-600",
      agent: "finance" as const,
    },
    {
      label: "General",
      color: "bg-amber-500",
      borderColor: "border-amber-600",
      agent: "general" as const,
    },
  ];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);

    // Read file as text
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setFileContent(content);
    };
    reader.onerror = () => {
      alert("Error reading file");
      setFileName(null);
      setFileContent(null);
    };
    reader.readAsText(file);
  };

  const handleSendMessage = async () => {
    if (!message.trim() && !fileContent) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: message || `Uploaded file: ${fileName}`,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setMessage("");
    const currentFileContent = fileContent;
    const currentFileName = fileName;
    setFileContent(null);
    setFileName(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }

    try {
      let response;
      const agentToUse = selectedAgent || "general";

      if (agentToUse === "customer") {
        response = await chatWithCustomerAgent(
          message || `Process this file: ${currentFileName}`,
          sessionId || undefined,
          currentFileContent || undefined
        );
      } else if (agentToUse === "finance") {
        response = await chatWithFinanceAgent(
          message || `Process this file: ${currentFileName}`,
          sessionId || undefined,
          currentFileContent || undefined
        );
      } else {
        response = await chatWithAgent(
          message || `Process this file: ${currentFileName}`,
          sessionId || undefined,
          currentFileContent || undefined
        );
      }

      if (response.session_id) {
        setSessionId(response.session_id);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Failed to send message"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleBubbleClick = (agent: "general" | "customer" | "finance") => {
    setSelectedAgent(agent);
    // Optionally send a message when clicking a bubble
    // For now, just set the agent type
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 text-gray-100 px-6 py-4">
      {/* HEADER */}
      <h1 className="text-2xl mb-6 text-gray-900 font-medium">Hi {username}! </h1>

      {/* SCROLLABLE CENTER AREA */}
      <div className="flex-1 overflow-y-auto flex flex-col items-center space-y-6 mb-3">
        {/* Show messages if any, otherwise show initial prompt */}
        {messages.length > 0 ? (
          <div className="w-full max-w-4xl space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
                    msg.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-white text-gray-800 border border-gray-200"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  <p className="text-xs mt-2 opacity-60">
                    {msg.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white rounded-2xl p-4 flex items-center gap-2 border border-gray-200 shadow-sm">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                  <span className="text-gray-600 text-sm">Just a moment...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        ) : (
          <>
            {/* PROMPT */}
            <h2 className="text-xl text-gray-900 mb-6 font-medium">
              What would you like to explore today? 
            </h2>

            {/* BLOCKS */}
            <div className="flex gap-6">
              {bubbles.map((b) => (
                <motion.div
                  key={b.label}
                  whileHover={{ scale: 1.05 }}
                  onClick={() => handleBubbleClick(b.agent)}
                  className={`relative w-52 h-40 rounded-2xl bg-white border border-gray-200 shadow-sm hover:shadow-md flex flex-col justify-between p-4 cursor-pointer transition-all ${
                    selectedAgent === b.agent ? "ring-2 ring-offset-2 ring-offset-gray-50 ring-blue-400 shadow-md" : ""
                  }`}
                >
                  <span className="text-gray-800 font-medium text-sm">
                    {b.label}
                  </span>

                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    className={`flex items-center justify-center cursor-pointer w-10 h-10 rounded-lg ${b.color}`}
                    title={`Select ${b.label} agent`}
                  >
                    <Maximize2 className="w-5 h-5 text-gray-900" />
                  </motion.button>
                  {/* ACCENT BAR */}
                  <div
                    className={`absolute right-2 h-[80%] w-1.5 rounded-xl ${b.color}`}
                  ></div>
                </motion.div>
              ))}
            </div>

            {/* ADDITIONAL TEXT */}
            <div className="max-w-xl text-left text-gray-700 mb-3">
              <p className="mb-2 text-base leading-relaxed">
                You can{" "}
                <span className="font-medium text-gray-900">
                  choose a category above
                </span>{" "}
                to get started, or simply upload a file and I'll help organize it for you!
              </p>
              <p className="text-base leading-relaxed">
                Curious about what each category does?{" "}
                <span className="font-medium text-gray-900">Click any card to learn more!</span>
              </p>
            </div>
          </>
        )}
      </div>

      {/* FLOATING BUBBLES - Show when messages exist */}
      {messages.length > 0 && (
        <div className="flex justify-start gap-4 mb-3">
          {bubbles.map((b) => (
            <motion.button
              key={b.label}
              whileHover={{ scale: 1.1 }}
              onClick={() => handleBubbleClick(b.agent)}
              className={`flex items-center justify-center rounded-full px-4 py-2 text-sm font-medium ${b.color} border-2 ${b.borderColor} text-gray-900 ${
                selectedAgent === b.agent ? "ring-2 ring-offset-2 ring-offset-gray-200 ring-gray-900" : ""
              }`}
            >
              {b.label}
            </motion.button>
          ))}
        </div>
      )}

      {/* Selected agent indicator */}
      {selectedAgent && (
        <div className="mb-2 text-sm text-gray-600 flex items-center gap-2">
          <span className="text-gray-500">Using:</span>
          <span className="font-medium text-gray-800">{bubbles.find((b) => b.agent === selectedAgent)?.label || "General"}</span>
        </div>
      )}

      {/* File indicator */}
      {fileName && (
        <div className="mb-2 text-sm text-gray-600 flex items-center gap-2">
          <span className="text-gray-500">📎</span>
          <span className="font-medium text-gray-800">{fileName}</span>
          <span className="text-gray-500">ready</span>
        </div>
      )}

      {/* TEXT INPUT */}
      <div className="relative flex items-center bg-white border border-gray-300 rounded-full px-4 py-3 shadow-sm hover:shadow-md transition-shadow focus-within:ring-2 focus-within:ring-blue-400 focus-within:border-blue-400">
        <input
          type="text"
          placeholder="Ask me anything..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
          className="flex-1 bg-transparent focus:outline-none text-gray-800 placeholder-gray-400 disabled:opacity-50"
        />
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt,.pdf,.csv,.json"
          onChange={handleFileUpload}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="flex items-center justify-center w-8 h-8 rounded-full hover:bg-gray-100 transition mr-2"
          title="Upload file"
          disabled={loading}
        >
          <Plus className="w-5 h-5 text-gray-600" />
        </button>
        <button
          onClick={handleSendMessage}
          disabled={loading || (!message.trim() && !fileContent)}
          className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500 hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-500"
          title="Send message"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 text-white animate-spin" />
          ) : (
            <Send className="w-5 h-5 text-white" />
          )}
        </button>
      </div>
    </div>
  );
}
