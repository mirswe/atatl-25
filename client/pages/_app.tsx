import "@/styles/globals.css";
import type { AppProps } from "next/app";
import Sidebar from "@/components/Sidebar";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className="flex h-screen">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <main className="flex-1 overflow-y-auto bg-gray-50 p-1">
          <Component {...pageProps} />
        </main>
      </div>
    </div>
  );
}
