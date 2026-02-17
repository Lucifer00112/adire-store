const api = {
    // Replace with your Render URL once deployment is complete
    baseUrl: window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:5000'
        : 'https://adire-store.onrender.com',

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add Authorization header if user is logged in
        const user = window.auth.getUser();
        if (user && user.password && !headers['Authorization']) {
            // For simple admin auth, we use the password as the token for now
            headers['Authorization'] = `Bearer ${user.password}`;
        }

        const response = await fetch(url, {
            ...options,
            headers
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || result.message || 'API request failed');
        }
        return result;
    },

    async get(endpoint, options = {}) {
        const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return await this.request(path, { method: 'GET', ...options });
    },

    async post(endpoint, data, options = {}) {
        const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return await this.request(path, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    },

    async put(endpoint, data, options = {}) {
        const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return await this.request(path, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    },

    async delete(endpoint, options = {}) {
        const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
        return await this.request(path, { method: 'DELETE', ...options });
    }
};


window.api = api;

