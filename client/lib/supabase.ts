import { createClient, SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl: string = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey: string = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn(
    "Supabase environment variables are not set. Please check your .env file."
  );
}

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);

// Server-side client for getServerSideProps
export const createServerClient = (): SupabaseClient => {
  return createClient(supabaseUrl, supabaseAnonKey);
};


