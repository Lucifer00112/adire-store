const auth = {
    async register(name, email, password) {
        return await window.api.post('/register', { name, email, password });
    },

    async verify(email, code, remember = true) {
        const result = await window.api.post('/verify', { email, code });
        if (result.user) {
            const storage = remember ? localStorage : sessionStorage;
            storage.setItem('user', JSON.stringify(result.user));
            if (window.cart) window.cart.init();
        }
        return result;
    },

    async login(email, password, remember = true) {
        const result = await window.api.post('/login', { email, password });
        if (result.user) {
            const storage = remember ? localStorage : sessionStorage;
            storage.setItem('user', JSON.stringify(result.user));
            if (window.cart) window.cart.init();
        }
        return result;
    },

    logout() {
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
        if (window.cart) window.cart.init();
        window.location.href = '/frontend-adire/index.html';
    },

    getUser() {
        const user = localStorage.getItem('user') || sessionStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    async updateProfile(data) {
        const user = this.getUser();
        if (!user) throw new Error('Not logged in');
        const res = await window.api.put(`/user/profile?email=${user.email}`, data);
        // Refresh local user data
        const updated = await window.api.get(`/user/profile?email=${user.email}`);
        const storage = localStorage.getItem('user') ? localStorage : sessionStorage;
        storage.setItem('user', JSON.stringify(updated));
        return res;
    },

    async changePassword(oldPassword, newPassword) {
        const user = this.getUser();
        if (!user) throw new Error('Not logged in');
        return await window.api.post('/user/change-password', {
            email: user.email,
            old_password: oldPassword,
            new_password: newPassword
        });
    },

    isLoggedIn() {
        return !!this.getUser();
    }
};

window.auth = auth;
