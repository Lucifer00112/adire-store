const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Authentication middleware
const auth = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      // For development, create mock user if no token
      req.user = { _id: 'dev_user_id', role: 'customer' };
      return next();
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Try to find user
    const user = await User.findById(decoded.userId);
    
    if (user) {
      req.user = user;
      req.token = token;
      return next();
    }

    // If user not found, still continue with mock user
    req.user = { _id: decoded.userId, role: 'customer' };
    next();
  } catch (error) {
    // For development, continue anyway
    req.user = { _id: 'dev_user_id', role: 'customer' };
    next();
  }
};

module.exports = { auth };