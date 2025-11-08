// example page with server-side data fetching (idk how to use this)
import { GetServerSideProps } from "next";
import { createServerClient } from "@/lib/supabase";
import { ExampleData } from "@/types";

interface ExamplePageProps {
  data: ExampleData[];
  error?: string;
}

export default function ExamplePage({ data, error }: ExamplePageProps) {
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Example Page</h1>
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-200">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Example Page with Server-Side Data</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        This page demonstrates fetching data using getServerSideProps with Supabase.
      </p>

      {data.length === 0 ? (
        <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-200">
          No data found. Make sure your Supabase connection is configured correctly.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data.map((item) => (
            <div
              key={item.id}
              className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
            >
              <h2 className="text-xl font-semibold mb-2">{item.title}</h2>
              {item.description && (
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {item.description}
                </p>
              )}
              <p className="text-sm text-gray-500 dark:text-gray-500">
                Created: {new Date(item.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export const getServerSideProps: GetServerSideProps<ExamplePageProps> = async () => {
  try {
    const supabase = createServerClient();

    // Example: Fetch data from a table called 'examples'
    // Replace 'examples' with your actual table name
    const { data, error } = await supabase
      .from("examples")
      .select("*")
      .limit(10);

    if (error) {
      console.error("Supabase error:", error);
      // Return empty array if table doesn't exist (for development)
      return {
        props: {
          data: [],
          error: error.message,
        },
      };
    }

    // Type assertion with validation
    const typedData: ExampleData[] = (data || []).map((item: unknown) => ({
      id: (item as ExampleData).id || "",
      title: (item as ExampleData).title || "",
      description: (item as ExampleData).description,
      created_at: (item as ExampleData).created_at || new Date().toISOString(),
    }));

    return {
      props: {
        data: typedData,
      },
    };
  } catch (error) {
    console.error("Error fetching data:", error);
    return {
      props: {
        data: [],
        error: error instanceof Error ? error.message : "Unknown error",
      },
    };
  }
};


