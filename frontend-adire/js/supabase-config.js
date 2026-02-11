/**
 * SUPABASE CONFIGURATION
 * Replace the placeholder values with your actual Supabase Project URL and Public API Key.
 * You can find these in your Supabase Dashboard under Project Settings > API.
 */
const SUPABASE_URL = "https://fhnaialqfslxskroendg.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZobmFpYWxxZnNseHNrcm9lbmRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA4MDg3ODEsImV4cCI6MjA4NjM4NDc4MX0.eqJ8Jc903FEMKwWRpbwNCmJmPQgTvpjVWRbNfsoYYf8";

// Initialize the Supabase client
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Make it globally available
window.supabase = supabaseClient;
