const express = require('express');
const router = express.Router();

// Sample products data
const sampleProducts = [
  {
    id: '1',
    name: 'Traditional Adire Buba',
    slug: 'traditional-adire-buba',
    price: 15000,
    category: 'women',
    description: 'Hand-dyed traditional Yoruba Adire',
    images: ['https://via.placeholder.com/400'],
    sizes: ['S', 'M', 'L'],
    colors: ['Indigo', 'White'],
    stock: 10
  },
  {
    id: '2',
    name: 'Modern Adire T-Shirt',
    slug: 'modern-adire-tshirt',
    price: 8000,
    category: 'unisex',
    description: 'Contemporary Adire print t-shirt',
    images: ['https://via.placeholder.com/400'],
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Black', 'Navy'],
    stock: 25
  }
];

// Get all products
router.get('/', (req, res) => {
  const { category } = req.query;
  let products = sampleProducts;
  
  if (category) {
    products = products.filter(p => p.category === category);
  }
  
  res.json({
    success: true,
    count: products.length,
    products
  });
});

// Get single product
router.get('/:slug', (req, res) => {
  const product = sampleProducts.find(p => p.slug === req.params.slug);
  
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
});

module.exports = router;