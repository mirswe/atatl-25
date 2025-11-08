import Link from "next/link";

export default function Navigation(): React.ReactElement {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/80 backdrop-blur-sm dark:border-gray-800 dark:bg-gray-900/80">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center">
          <Link href="/" className="text-xl font-bold">
            Hackathon App
          </Link>
        </div>
      </div>
    </nav>
  );
}


