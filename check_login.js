
const { createClient } = require('@supabase/supabase-js');

// Values from your supabase-config.js
const SUPABASE_URL = "https://fhnaialqfslxskroendg.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZobmFpYWxxZnNseHNrcm9lbmRnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA4MDg3ODEsImV4cCI6MjA4NjM4NDc4MX0.eqJ8Jc903FEMKwWRpbwNCmJmPQgTvpjVWRbNfsoYYf8";

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function checkLogin(email, password) {
    console.log(`\n🔍 TESTING LOGIN FOR: ${email}`);
    console.log(`-----------------------------------`);

    const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
    });

    if (error) {
        console.error("❌ LOGIN FAILED!");
        console.error("Error Message:", error.message);
        console.error("\nREASON: This means Supabase does not recognize this password for this email.");
    } else {
        console.log("✅ LOGIN SUCCESSFUL!");
        console.log("User ID:", data.user.id);

        // Check profile role
        const { data: profile, error: pError } = await supabase
            .from('profiles')
            .select('role')
            .eq('id', data.user.id)
            .single();

        if (pError) {
            console.error("❌ FAILED TO GET PROFILE:", pError.message);
        } else {
            console.log("👤 USER ROLE:", profile.role);
            if (profile.role === 'admin') {
                console.log("👑 ADMIN ACCESS CONFIRMED.");
            } else {
                console.log("⚠️ WARNING: You are NOT an admin in the profiles table.");
            }
        }
    }
}

// Get credentials from command line
const email = process.argv[2];
const password = process.argv[3];

if (!email || !password) {
    console.log("Usage: node check_login.js your-email@gmail.com your-password");
} else {
    checkLogin(email, password);
}
