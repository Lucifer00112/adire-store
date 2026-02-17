/**
 * SUPABASE CONFIGURATION
 * Replace the placeholder values with your actual Supabase Project URL and Public API Key.
 * You can find these in your Supabase Dashboard under Project Settings > API.
 */
const SUPABASE_URL = "https://dwfmoufacboipjwxsmoz.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3Zm1vdWZhY2JvaXBqd3hzbW96Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEyNTA3NjksImV4cCI6MjA4NjgyNjc2OX0.WVZ4j6BXGj6fagK3vKBc4aMfSzfBzntDmyrAr0SAouQ";

// Initialize the Supabase client
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Make it globally available
window.supabase = supabaseClient;
