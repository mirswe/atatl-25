import Link from "next/link";

export default function Navigation(): React.ReactElement {
  return (
    <nav className="sticky top-0 z-10 w-full bg-gray-100 border-b border-gray-200">
      <div className="h-15">
        <div className="flex h-16 items-center justify-end pr-10">
          <Link href="/" className="text-xl font-bold text-gray-900">
            Hackathon App
          </Link>
        </div>
      </div>
    </nav>
  );
}
