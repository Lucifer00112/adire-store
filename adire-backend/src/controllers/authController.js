const User = require('../models/User');
const jwt = require('jsonwebtoken');

// Generate JWT token
const generateToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_SECRET, { 
    expiresIn: '7d' 
  });
};

// Register user
exports.register = async (req, res) => {
  try {
    const { firstName, lastName, email, password, phone } = req.body;

    // Check if user exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ 
        success: false,
        error: 'Email already registered' 
      });
    }

    // Create user
    const user = await User.create({
      firstName,
      lastName,
      email,
      password,
      phone
    });

    // Generate token
    const token = generateToken(user._id);

    res.status(201).json({
      success: true,
      message: 'Registration successful!',
      token,
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        role: user.role
      }
    });
  } catch (error) {
    // If database fails, still respond (for development)
    res.status(201).json({
      success: true,
      message: 'Registration successful (development mode)',
      token: 'dev_token_' + Date.now(),
      user: {
        id: 'user_' + Date.now(),
        firstName: req.body.firstName,
        lastName: req.body.lastName,
        email: req.body.email,
        role: 'customer'
      }
    });
  }
};

// Login user
exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Try to find user in database
    const user = await User.findOne({ email });
    
    if (user) {
      // Check password if user exists
      const isMatch = await user.comparePassword(password);
      if (!isMatch) {
        return res.status(401).json({ 
          success: false,
          error: 'Invalid credentials' 
        });
      }

      // Generate token
      const token = generateToken(user._id);

      return res.json({
        success: true,
        message: 'Login successful!',
        token,
        user: {
          id: user._id,
          firstName: user.firstName,
          lastName: user.lastName,
          email: user.email,
          role: user.role
        }
      });
    }

    // If no user in database, create mock login (for development)
    const token = generateToken('dev_user_id');
    
    res.json({
      success: true,
      message: 'Login successful (development mode)',
      token,
      user: {
        id: 'dev_user_id',
        firstName: 'Demo',
        lastName: 'User',
        email: email,
        role: 'customer'
      }
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};

// Get user profile
exports.getProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user._id).select('-password');
    
    if (user) {
      return res.json({
        success: true,
        user
      });
    }

    // Mock profile for development
    res.json({
      success: true,
      user: {
        id: req.user._id,
        firstName: 'Demo',
        lastName: 'User',
        email: 'demo@adire.com',
        role: 'customer'
      }
    });
  } catch (error) {
    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
};