const auth = {
    // Current session/user cache
    currentUser: null,

    async register(name, email, password) {
        const { data, error } = await window.supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    full_name: name
                }
            }
        });
        if (error) throw error;
        return data;
    },

    async login(email, password, remember = true) {
        const { data, error } = await window.supabase.auth.signInWithPassword({
            email,
            password
        });
        if (error) throw error;

        // Supabase handles persistence, but we can set a helper for our UI
        this.currentUser = data.user;
        if (window.cart) window.cart.init();
        return { success: true, user: data.user };
    },

    async logout() {
        const { error } = await window.supabase.auth.signOut();
        if (error) throw error;
        this.currentUser = null;
        if (window.cart) window.cart.init();
        window.location.href = '/frontend-adire/index.html';
    },

    getUser() {
        // Supabase stores the session in localStorage under a key like 'sb-[project-id]-auth-token'
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('sb-') && key.endsWith('-auth-token')) {
                const session = JSON.parse(localStorage.getItem(key));
                return session ? session.user : null;
            }
        }
        return this.currentUser; // Fallback to memory if session not found yet
    },

    async getUserProfile() {
        const user = this.getUser();
        if (!user) return null;
        const { data, error } = await window.supabase
            .from('profiles')
            .select('*')
            .eq('id', user.id)
            .single();
        if (error) throw error;
        return data;
    },

    async updateProfile(data) {
        const user = this.getUser();
        if (!user) throw new Error('Not logged in');
        const { error } = await window.supabase
            .from('profiles')
            .update(data)
            .eq('id', user.id);
        if (error) throw error;
        return { success: true };
    },

    async changePassword(newPassword) {
        const { error } = await window.supabase.auth.updateUser({
            password: newPassword
        });
        if (error) throw error;
        return { success: true };
    },

    async resetPassword(email) {
        // Construct the redirect URL for the reset password page
        // Since we moved to the root, the path should be relative to the site origin
        const resetUrl = `${window.location.origin}/pages/reset-password.html`;

        const { error } = await window.supabase.auth.resetPasswordForEmail(email, {
            redirectTo: resetUrl,
        });
        if (error) throw error;
        return { success: true };
    },

    isLoggedIn() {
        return !!this.getUser();
    }
};

window.auth = auth;
