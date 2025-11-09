import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { useRouter } from "next/router";
import Navigation from "@/components/Navigation";
import Sidebar from "@/components/Sidebar";

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();

  const noLayoutRoutes = ["/login", "/signup"];

  const hideLayout = noLayoutRoutes.includes(router.pathname);

  if (hideLayout) {
    return <Component {...pageProps} />;
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navigation />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-1">
          <Component {...pageProps} />
        </main>
      </div>
    </div>
  );
}
