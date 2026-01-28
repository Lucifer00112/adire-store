const API_BASE_URL = (window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '' ||
    window.location.protocol === 'file:')
    ? 'http://127.0.0.1:5000'
    : 'https://adire-backend.vercel.app';

const api = {
    async post(endpoint, data, headers = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Something went wrong');
            return result;
        } catch (error) {
            console.error(`API POST Error [${endpoint}]:`, error);
            throw error;
        }
    },

    async get(endpoint, headers = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'GET',
                headers: {
                    ...headers
                }
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Something went wrong');
            return result;
        } catch (error) {
            console.error(`API GET Error [${endpoint}]:`, error);
            throw error;
        }
    },

    async put(endpoint, data, headers = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Something went wrong');
            return result;
        } catch (error) {
            console.error(`API PUT Error [${endpoint}]:`, error);
            throw error;
        }
    },

    async delete(endpoint, headers = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'DELETE',
                headers: {
                    ...headers
                }
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Something went wrong');
            return result;
        } catch (error) {
            console.error(`API DELETE Error [${endpoint}]:`, error);
            throw error;
        }
    },
    baseUrl: API_BASE_URL
};

window.api = api;
