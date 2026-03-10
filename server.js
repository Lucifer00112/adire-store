require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const mongoose = require('mongoose');
const cloudinary = require('cloudinary').v2;
const { CloudinaryStorage } = require('multer-storage-cloudinary');
const multer = require('multer');
const dns = require('dns');

// Force Node.js to use Google DNS to bypass local network SRV resolution issues
dns.setServers(['8.8.8.8', '8.8.4.4']);

const app = express();
const PORT = process.env.PORT || 3001;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

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
function requireAdmin(req, res, next) {
    const password = req.headers['x-admin-password'] || req.query.password;
    if (password === ADMIN_PASSWORD) {
        next();
    } else {
        res.status(401).json({ error: 'Unauthorized. Invalid admin password.' });
    }
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

// Verify admin password
app.post('/api/admin/verify', requireAdmin, (req, res) => {
    res.json({ success: true, message: 'Authenticated' });
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
