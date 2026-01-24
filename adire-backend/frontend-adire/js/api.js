const API_BASE_URL = 'http://localhost:5000';

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
    }
};

window.api = api;
