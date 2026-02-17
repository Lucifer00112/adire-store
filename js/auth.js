const auth = {
    // Current session/user cache
    currentUser: null,

    async register(name, email, password) {
        const response = await window.api.post('/register', { name, email, password });
        return response;
    },

    async resendVerificationCode(email) {
        return await window.api.post('/resend-code', { email });
    },

    async verify(email, code, remember = true) {
        const response = await window.api.post('/verify', { email, code });
        if (response.user) {
            this.saveUser(response.user);
        }
        return response;
    },

    async login(email, password, remember = true) {
        const response = await window.api.post('/login', { email, password });
        if (response.user) {
            // Include password in saved object for simple Bearer auth simulation if needed
            response.user.password = password;
            if (remember) {
                this.saveUser(response.user);
            } else {
                this.currentUser = response.user;
            }
        }
        return response;
    },

    async logout() {
        localStorage.removeItem('adire_user');
        this.currentUser = null;
        window.location.href = '/index.html';
    },

    saveUser(user) {
        localStorage.setItem('adire_user', JSON.stringify(user));
        this.currentUser = user;
    },

    getUser() {
        if (this.currentUser) return this.currentUser;
        const saved = localStorage.getItem('adire_user');
        if (saved) {
            try {
                this.currentUser = JSON.parse(saved);
                return this.currentUser;
            } catch (e) {
                localStorage.removeItem('adire_user');
            }
        }
        return null;
    },

    async getUserProfile() {
        const user = this.getUser();
        if (!user) return null;
        // The backend returns profile info in the login/profile endpoints
        return await window.api.get(`/user/profile?email=${user.email}`);
    },

    async updateProfile(data) {
        const user = this.getUser();
        if (!user) throw new Error('Not logged in');
        return await window.api.put(`/user/profile?email=${user.email}`, data);
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

