// This file adds sample Adire products to your database
console.log('Starting to add Adire products...');

// Simple version without mongoose (in case mongoose has issues)
const products = [
  {
    name: "Adire Ankara Maxi Dress",
    price: 18500,
    description: "Beautiful hand-dyed Adire Ankara fabric",
    category: "women",
    sizes: ["S", "M", "L", "XL"],
    colors: ["Blue & White", "Red & Gold", "Purple & Yellow"],
    stock: 10
  },
  {
    name: "Adire Agbada for Men",
    price: 35000,
    description: "Traditional Nigerian Agbada",
    category: "men",
    sizes: ["M", "L", "XL", "XXL"],
    colors: ["White & Blue", "Gold & Brown", "Green & Black"],
    stock: 5
  },
  {
    name: "Adire Head Tie (Gele)",
    price: 8000,
    description: "Elegant head tie for traditional events",
    category: "accessories",
    colors: ["Gold", "Blue", "Red", "Purple"],
    stock: 20
  }
];

console.log('✅ Sample products created in memory');
console.log('📦 Total products:', products.length);
console.log('👗 Women:', products.filter(p => p.category === 'women').length);
console.log('👔 Men:', products.filter(p => p.category === 'men').length);
console.log('🎀 Accessories:', products.filter(p => p.category === 'accessories').length);

// Check if mongoose is available
try {
  const mongoose = require('mongoose');
  require('dotenv').config();
  
  console.log('\n📡 Connecting to MongoDB Atlas...');
  
  mongoose.connect(process.env.MONGO_URI)
    .then(async () => {
      console.log('✅ Connected to MongoDB Atlas');
      
      // Define product schema WITHOUT slug for now
      const productSchema = new mongoose.Schema({
        name: String,
        price: Number,
        description: String,
        category: String,
        sizes: [String],
        colors: [String],
        stock: Number,
        featured: { type: Boolean, default: false },
        discount: { type: Number, default: 0 },
        createdAt: { type: Date, default: Date.now }
      });
      
      // Create temporary model
      const Product = mongoose.model('TempProduct', productSchema);
      
      // Clear old products using temporary model
      await Product.deleteMany({});
      console.log('✅ Cleared old products');
      
      // Add new products
      await Product.insertMany(products);
      console.log(`✅ Added ${products.length} Adire products to database!`);
      
      // Show what was added
      const dbProducts = await Product.find();
      console.log('\n📊 PRODUCTS IN YOUR DATABASE:');
      console.log('=============================');
      dbProducts.forEach((p, i) => {
        console.log(`${i+1}. ${p.name}`);
        console.log(`   Price: ₦${p.price.toLocaleString()}`);
        console.log(`   Stock: ${p.stock} available`);
        console.log(`   Category: ${p.category}`);
        console.log('   ---');
      });
      
      mongoose.connection.close();
      console.log('\n🎉 SUCCESS! Your Adire store now has products!');
      console.log('👉 Check: http://localhost:5000/api/products');
      
    })
    .catch(error => {
      console.log('❌ Database error:', error.message);
      console.log('💡 But you still have products in memory!');
    });
    
} catch (error) {
  console.log('⚠️  Could not use mongoose, showing sample products:');
  console.log('📦 Products available:', products.length);
}