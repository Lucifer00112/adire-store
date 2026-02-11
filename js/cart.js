const cart = {
    items: [],

    getStorageKey() {
        if (window.auth && typeof window.auth.getUser === 'function') {
            const user = window.auth.getUser();
            if (user && user.email) {
                return `adire_cart_${user.email}`;
            }
        }
        return 'adire_cart_guest';
    },

    init() {
        const key = this.getStorageKey();
        const savedCart = localStorage.getItem(key);
        if (savedCart) {
            this.items = JSON.parse(savedCart);
        } else {
            this.items = [];
        }
        this.updateUI();
    },

    addItem(product) {
        const existingItem = this.items.find(item => item.id === product.id);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({ ...product, quantity: 1 });
        }
        this.save();
        this.updateUI();
        this.notify(`Added ${product.name} to cart`);
    },

    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.save();
        this.updateUI();
    },

    updateQuantity(productId, delta) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            item.quantity += delta;
            if (item.quantity <= 0) {
                this.removeItem(productId);
            } else {
                this.save();
                this.updateUI();
            }
        }
    },

    clear() {
        this.items = [];
        this.save();
        this.updateUI();
    },

    getTotal() {
        return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    },

    getCount() {
        return this.items.reduce((sum, item) => sum + item.quantity, 0);
    },

    save() {
        const key = this.getStorageKey();
        localStorage.setItem(key, JSON.stringify(this.items));
    },

    updateUI() {
        const badge = document.getElementById('cart-badge');
        if (badge) {
            badge.innerText = this.getCount();
            badge.style.display = this.getCount() > 0 ? 'flex' : 'none';
        }
        // Dispatch custom event for pages that need to update independently
        window.dispatchEvent(new CustomEvent('cartUpdated'));
    },

    notify(message) {
        const toast = document.createElement('div');
        toast.className = 'glass-panel';
        toast.style.cssText = `
            position: fixed; bottom: 20px; right: 20px;
            padding: 15px 25px; background: var(--primary-indigo);
            color: white; border-radius: 8px; z-index: 2000;
            box-shadow: var(--card-shadow); animation: slideUp 0.3s ease-out;
        `;
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
};

// Add slideUp animation to CSS if not present
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from { transform: translateY(100%); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

window.cart = cart;
cart.init();
