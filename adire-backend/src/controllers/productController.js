const Product = require('../models/Product');

// ========== SIMPLE VERSION - FOR BASIC OPERATIONS ==========

// 1. GET ALL PRODUCTS (Public)
exports.getAllProducts = async (req, res) => {
  try {
    const products = await Product.find({});
    
    res.json({
      success: true,
      count: products.length,
      products
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};

// 2. GET FEATURED PRODUCTS (Public)
exports.getFeaturedProducts = async (req, res) => {
  try {
    const featuredProducts = await Product.find({ isFeatured: true })
      .limit(8)
      .select('name slug price images category rating');
    
    res.json({
      success: true,
      featuredProducts
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};

// ========== YOUR EXISTING FUNCTIONS (Updated) ==========

// 3. GET ONE PRODUCT BY SLUG (Public)
exports.getProductBySlug = async (req, res) => {
  try {
    const product = await Product.findOne({ slug: req.params.slug });

    if (!product) {
      return res.status(404).json({ 
        success: false,
        error: 'Product not found' 
      });
    }

    res.json({
      success: true,
      product
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};

// 4. CREATE PRODUCT (Admin only - will add auth later)
exports.createProduct = async (req, res) => {
  try {
    const {
      name,
      description,
      price,
      category,
      stock
    } = req.body;

    // Generate slug from name
    const slug = name.toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');

    // Simple image handling (skip Cloudinary for now)
    const images = [];

    const product = await Product.create({
      name,
      slug,
      description,
      price: Number(price),
      category,
      images,
      stock: Number(stock),
      // Optional fields with defaults
      colors: req.body.colors || [],
      sizes: req.body.sizes || [],
      tags: req.body.tags ? req.body.tags.split(',') : []
    });

    res.status(201).json({
      success: true,
      message: 'Product created successfully',
      product
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};

// 5. UPDATE PRODUCT (Admin only)
exports.updateProduct = async (req, res) => {
  try {
    const updates = req.body;
    const productId = req.params.id;

    // Update slug if name is being updated
    if (updates.name) {
      updates.slug = updates.name.toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)/g, '');
    }

    const product = await Product.findByIdAndUpdate(
      productId,
      updates,
      { new: true, runValidators: true }
    );

    if (!product) {
      return res.status(404).json({ 
        success: false,
        error: 'Product not found' 
      });
    }

    res.json({
      success: true,
      message: 'Product updated successfully',
      product
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};

// 6. DELETE PRODUCT (Admin only)
exports.deleteProduct = async (req, res) => {
  try {
    const product = await Product.findByIdAndDelete(req.params.id);

    if (!product) {
      return res.status(404).json({ 
        success: false,
        error: 'Product not found' 
      });
    }

    // Skip Cloudinary deletion for now
    // We'll add image cleanup later

    res.json({
      success: true,
      message: 'Product deleted successfully'
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};

// 7. ADD PRODUCT REVIEW (Logged in users)
exports.addReview = async (req, res) => {
  try {
    const { rating, comment } = req.body;
    const productId = req.params.id;

    const product = await Product.findById(productId);

    if (!product) {
      return res.status(404).json({ 
        success: false,
        error: 'Product not found' 
      });
    }

    // Check if user already reviewed (simplified for now)
    // We'll add user auth later
    const existingReview = product.reviews.find(
      review => review.user && review.user.toString() === 'temp-user-id'
    );

    if (existingReview) {
      return res.status(400).json({ 
        success: false,
        error: 'You have already reviewed this product' 
      });
    }

    const review = {
      user: 'temp-user-id', // Will replace with actual user ID later
      rating: Number(rating),
      comment,
      createdAt: new Date()
    };

    product.reviews.push(review);

    // Update product rating
    const totalReviews = product.reviews.length;
    const sumRatings = product.reviews.reduce((sum, review) => sum + review.rating, 0);
    product.rating = sumRatings / totalReviews;

    await product.save();

    res.status(201).json({
      success: true,
      message: 'Review added successfully',
      review
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};

// 8. GET RELATED PRODUCTS (Public)
exports.getRelatedProducts = async (req, res) => {
  try {
    const product = await Product.findById(req.params.id);

    if (!product) {
      return res.status(404).json({ 
        success: false,
        error: 'Product not found' 
      });
    }

    const relatedProducts = await Product.find({
      $or: [
        { category: product.category },
        { tags: { $in: product.tags } }
      ],
      _id: { $ne: product._id }
    })
    .limit(4)
    .select('name slug price images rating');

    res.json({
      success: true,
      relatedProducts
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};