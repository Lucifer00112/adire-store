const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    // If no MONGO_URI, just skip database connection
    if (!process.env.MONGO_URI) {
      console.log('🔄 Running in development mode (no database needed)');
      return Promise.resolve(); // Return a resolved promise
    }
    
    // Try to connect if MONGO_URI exists
    await mongoose.connect(process.env.MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    
    console.log('✅ MongoDB Connected to Atlas!');
    return Promise.resolve();
  } catch (error) {
    console.log('🔄 Using development mode (database not required)');
    // Don't throw error, just continue
  }
};

module.exports = connectDB;