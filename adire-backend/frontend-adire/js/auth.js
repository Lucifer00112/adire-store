const auth = {
    async register(name, email, password) {
        return await window.api.post('/register', { name, email, password });
    },

    async verify(email, code) {
        const result = await window.api.post('/verify', { email, code });
        if (result.user) {
            localStorage.setItem('user', JSON.stringify(result.user));
        }
        return result;
    },

    async login(email, password) {
        const result = await window.api.post('/login', { email, password });
        if (result.user) {
            localStorage.setItem('user', JSON.stringify(result.user));
        }
        return result;
    },

    logout() {
        localStorage.removeItem('user');
        window.location.href = '/frontend-adire/index.html';
    },

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isLoggedIn() {
        return !!this.getUser();
    }
};

window.auth = auth;
