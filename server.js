require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const mongoose = require('mongoose');
const cloudinary = require('cloudinary').v2;
const { CloudinaryStorage } = require('multer-storage-cloudinary');
const multer = require('multer');
const dns = require('dns');
const { Pool } = require('pg');

// Force Node.js to use Google DNS to bypass local network SRV resolution issues
dns.setServers(['8.8.8.8', '8.8.4.4']);

const app = express();
const PORT = process.env.PORT || 3001;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

// --- NEON POSTGRESQL CONNECT ---
const pgPool = new Pool({
    connectionString: process.env.NEON_DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

pgPool.query(`
    CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
`).then(() => console.log('Admins table initialized in Neon DB'))
  .catch(err => console.error('Neon DB initialization error:', err));

// --- CLOUDINARY CONFIG ---
cloudinary.config({
    cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
    api_key: process.env.CLOUDINARY_API_KEY,
    api_secret: process.env.CLOUDINARY_API_SECRET,
});

// Cloudinary multer storage
const storage = new CloudinaryStorage({
    cloudinary: cloudinary,
    params: {
        folder: 'adire-store',
        allowed_formats: ['jpg', 'jpeg', 'png', 'webp', 'gif'],
    },
});
const upload = multer({ storage });

// --- MONGODB CONNECT ---
mongoose.connect(process.env.MONGODB_URI)
    .then(() => console.log('Connected to MongoDB Atlas'))
    .catch(err => console.error('MongoDB connection error:', err));

// --- PRODUCT SCHEMA ---
const productSchema = new mongoose.Schema({
    name: { type: String, required: true },
    description: { type: String, default: '' },
    price: { type: Number, required: true },
    image_url: { type: String, required: true },
    category: { type: String, default: '' },
    createdAt: { type: Date, default: Date.now },
});

const Product = mongoose.model('Product', productSchema);

// --- MIDDLEWARE ---
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// --- AUTH MIDDLEWARE ---
async function requireAdmin(req, res, next) {
    const password = req.headers['x-admin-password'] || req.query.password;
    const email = req.headers['x-admin-email'] || req.query.email;

    if (password === ADMIN_PASSWORD && !email) {
        return next();
    }

    if (email && password) {
        try {
            const result = await pgPool.query('SELECT id FROM admins WHERE email = $1 AND password = $2', [email, password]);
            if (result.rows.length > 0) {
                return next();
            }
        } catch (err) {
            console.error('Neon DB auth error:', err);
        }
    }
    
    res.status(401).json({ error: 'Unauthorized. Invalid admin credentials.' });
}

// --- PUBLIC ROUTES ---

// Get all products (public)
app.get('/api/products', async (req, res) => {
    try {
        const products = await Product.find().sort({ createdAt: -1 });
        res.json(products);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch products.' });
    }
});

// --- ADMIN ROUTES ---

// Verify admin credentials
app.post('/api/admin/verify', async (req, res) => {
    // We check headers first (so front-ends can pass it there cleanly), or body if they post normally
    const email = req.body.email || req.headers['x-admin-email'];
    const password = req.body.password || req.headers['x-admin-password'];
    
    // Check master password
    if (password === ADMIN_PASSWORD && !email) {
        return res.json({ success: true, message: 'Authenticated as Master' });
    }
    
    if (!email || !password) {
        return res.status(400).json({ success: false, message: 'Email and password required' });
    }
    
    // Check Neon DB
    try {
        const result = await pgPool.query('SELECT id FROM admins WHERE email = $1 AND password = $2', [email, password]);
        if (result.rows.length > 0) {
            res.json({ success: true, message: 'Authenticated', email: email });
        } else {
            res.status(401).json({ success: false, message: 'Invalid credentials' });
        }
    } catch (err) {
        console.error(err);
        res.status(500).json({ success: false, error: 'Database error' });
    }
});

// Admin Sign Up
app.post('/api/admin/signup', async (req, res) => {
    const { email, password } = req.body;
    if (!email || !password) {
        return res.status(400).json({ error: 'Email and password are required.' });
    }
    try {
        const existing = await pgPool.query('SELECT id FROM admins WHERE email = $1', [email]);
        if (existing.rows.length > 0) {
            return res.status(400).json({ error: 'Admin with this email already exists.' });
        }
        await pgPool.query('INSERT INTO admins (email, password) VALUES ($1, $2)', [email, password]);
        res.status(201).json({ message: 'Admin registered successfully' });
    } catch (err) {
        console.error('Signup error:', err);
        res.status(500).json({ error: 'Failed to register admin in Neon DB.' });
    }
});

// Get admin list
app.get('/api/admin/users', requireAdmin, async (req, res) => {
    try {
        const result = await pgPool.query('SELECT id, email, password, created_at FROM admins ORDER BY created_at DESC');
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch admin users from Neon' });
    }
});

// Add a product (with Cloudinary image upload)
app.post('/api/admin/products', requireAdmin, upload.single('image'), async (req, res) => {
    try {
        const { name, description, price, category } = req.body;
        let imageUrl = req.body.image_url;

        if (req.file) {
            imageUrl = req.file.path; // Cloudinary URL
        }

        if (!name || !price || !imageUrl) {
            return res.status(400).json({ error: 'Name, price, and an image are required.' });
        }

        const product = new Product({
            name,
            description: description || '',
            price: Number(price),
            image_url: imageUrl,
            category: category || '',
        });

        await product.save();
        res.status(201).json({ message: 'Product added successfully', product });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to add product.' });
    }
});

// Delete a product
app.delete('/api/admin/products/:id', requireAdmin, async (req, res) => {
    try {
        const product = await Product.findByIdAndDelete(req.params.id);
        if (!product) {
            return res.status(404).json({ error: 'Product not found.' });
        }
        res.json({ message: 'Product deleted successfully' });
    } catch (err) {
        res.status(500).json({ error: 'Failed to delete product.' });
    }
});

// Update a product
app.put('/api/admin/products/:id', requireAdmin, upload.single('image'), async (req, res) => {
    try {
        const updates = req.body;
        if (req.file) {
            updates.image_url = req.file.path;
        }
        const product = await Product.findByIdAndUpdate(req.params.id, updates, { new: true });
        if (!product) {
            return res.status(404).json({ error: 'Product not found.' });
        }
        res.json({ message: 'Product updated', product });
    } catch (err) {
        res.status(500).json({ error: 'Failed to update product.' });
    }
});

// --- PAGE ROUTES ---
// In development, the Vite server (port 3000) serves all React pages (/, /admin, etc.).
// The Express server (port 3001) only serves the API routes. 
// If building for production later, you would serve the static files from the build/dist folder here.

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Admin Password: ${ADMIN_PASSWORD}`);
});
