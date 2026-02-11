const api = {
    // Utility to handle Supabase responses
    async handleResponse({ data, error }) {
        if (error) {
            console.error("Supabase Error:", error);
            throw new Error(error.message);
        }
        return data;
    },

    // GET products/data
    async get(endpoint) {
        // Simple router for endpoints
        if (endpoint === '/products') {
            return await this.handleResponse(
                await window.supabase.from('products').select('*')
            );
        }

        if (endpoint.startsWith('/orders/')) {
            const email = endpoint.split('/orders/')[1];
            return await this.handleResponse(
                await window.supabase.from('orders').select('*').eq('user_email', email).order('created_at', { ascending: false })
            );
        }

        if (endpoint.startsWith('/user/profile')) {
            const user = window.auth.getUser();
            return await this.handleResponse(
                await window.supabase.from('profiles').select('*').eq('id', user.id).single()
            );
        }

        if (endpoint.startsWith('/track/')) {
            const orderId = endpoint.split('/track/')[1];
            return await this.handleResponse(
                await window.supabase.from('orders').select('*').ilike('id', `${orderId}%`).single()
            );
        }

        const table = endpoint.replace('/', '');
        return await this.handleResponse(
            await window.supabase.from(table).select('*')
        );
    },

    // POST data (Orders, Registration happens in auth.js)
    async post(endpoint, data) {
        if (endpoint === '/orders') {
            return await this.handleResponse(
                await window.supabase.from('orders').insert([data])
            );
        }

        const table = endpoint.replace('/', '');
        return await this.handleResponse(
            await window.supabase.from(table).insert([data])
        );
    },

    // PUT data
    async put(endpoint, data) {
        // Handle order confirmation
        if (endpoint.includes('/received')) {
            const orderId = endpoint.split('/orders/')[1].split('/')[0];
            return await this.handleResponse(
                await window.supabase.from('orders').update({
                    status: 'Delivered',
                    delivery_status: 'Delivered'
                }).eq('id', orderId)
            );
        }

        // For profile updates:
        if (endpoint.includes('/user/profile')) {
            const user = window.auth.getUser();
            return await this.handleResponse(
                await window.supabase.from('profiles').update(data).eq('id', user.id)
            );
        }

        const table = endpoint.split('/')[1];
        return await this.handleResponse(
            await window.supabase.from(table).update(data)
        );
    },

    async delete(endpoint) {
        const table = endpoint.replace('/', '');
        return await this.handleResponse(
            await window.supabase.from(table).delete()
        );
    }
};

window.api = api;
