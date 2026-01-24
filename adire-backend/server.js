const express = require('express');
const cors = require('cors');
const fs = require('fs');
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('frontend'));

// ==================== REAL DATABASE ====================
// Create database file if it doesn't exist
const DB_FILE = 'users.json';

// Initialize database
let usersDB = { users: [] };
if (fs.existsSync(DB_FILE)) {
  usersDB = JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
} else {
  fs.writeFileSync(DB_FILE, JSON.stringify(usersDB, null, 2));
}

// Save to database function
function saveToDB() {
  fs.writeFileSync(DB_FILE, JSON.stringify(usersDB, null, 2));
}

// ==================== REAL REGISTRATION ====================
app.post('/api/register', (req, res) => {
  const { firstName, lastName, email, password, phone } = req.body;
  
  // Check if user already exists
  const existingUser = usersDB.users.find(user => user.email === email);
  if (existingUser) {
    return res.status(400).json({
      success: false,
      message: 'User already exists'
    });
  }
  
  // Create new user
  const newUser = {
    id: 'user_' + Date.now(),
    firstName,
    lastName,
    email,
    password, // In real app, hash this password!
    phone,
    address: '',
    profilePicture: '',
    joinDate: new Date().toISOString(),
    orders: [],
    createdAt: new Date().toISOString()
  };
  
  // Save to database
  usersDB.users.push(newUser);
  saveToDB();
  
  // Return response (without password)
  const { password: _, ...userWithoutPassword } = newUser;
  
  res.json({
    success: true,
    message: 'Registration successful!',
    user: userWithoutPassword
  });
});

// ==================== REAL LOGIN ====================
app.post('/api/login', (req, res) => {
  const { email, password } = req.body;
  
  // Find user in database
  const user = usersDB.users.find(user => 
    user.email === email && user.password === password
  );
  
  if (!user) {
    return res.status(401).json({
      success: false,
      message: 'Invalid email or password'
    });
  }
  
  // Remove password from response
  const { password: _, ...userWithoutPassword } = user;
  
  res.json({
    success: true,
    message: 'Login successful!',
    user: userWithoutPassword
  });
});

// ==================== GET ALL USERS (for admin) ====================
app.get('/api/users', (req, res) => {
  // Remove passwords before sending
  const usersWithoutPasswords = usersDB.users.map(user => {
    const { password, ...rest } = user;
    return rest;
  });
  
  res.json({
    success: true,
    count: usersWithoutPasswords.length,
    users: usersWithoutPasswords
  });
});

// ==================== GET USER BY ID ====================
app.get('/api/users/:id', (req, res) => {
  const user = usersDB.users.find(user => user.id === req.params.id);
  
  if (!user) {
    return res.status(404).json({
      success: false,
      message: 'User not found'
    });
  }
  
  const { password, ...userWithoutPassword } = user;
  
  res.json({
    success: true,
    user: userWithoutPassword
  });
});

// ==================== UPDATE USER PROFILE ====================
app.put('/api/users/:id', (req, res) => {
  const userId = req.params.id;
  const updates = req.body;
  
  const userIndex = usersDB.users.findIndex(user => user.id === userId);
  
  if (userIndex === -1) {
    return res.status(404).json({
      success: false,
      message: 'User not found'
    });
  }
  
  // Update user
  usersDB.users[userIndex] = {
    ...usersDB.users[userIndex],
    ...updates,
    updatedAt: new Date().toISOString()
  };
  
  saveToDB();
  
  const { password, ...userWithoutPassword } = usersDB.users[userIndex];
  
  res.json({
    success: true,
    message: 'Profile updated successfully',
    user: userWithoutPassword
  });
});

// ==================== DELETE USER ====================
app.delete('/api/users/:id', (req, res) => {
  const userId = req.params.id;
  
  const userIndex = usersDB.users.findIndex(user => user.id === userId);
  
  if (userIndex === -1) {
    return res.status(404).json({
      success: false,
      message: 'User not found'
    });
  }
  
  // Remove user
  usersDB.users.splice(userIndex, 1);
  saveToDB();
  
  res.json({
    success: true,
    message: 'User deleted successfully'
  });
});

// ==================== OTHER ROUTES (keep your existing ones) ====================
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    usersCount: usersDB.users.length,
    timestamp: new Date().toISOString()
  });
});

app.get('/api/products', (req, res) => {
  const products = [
    {
      id: '1',
      name: "Traditional Adire Buba",
      price: 15000,
      category: "female",
      description: "Hand-dyed traditional Yoruba Adire Buba",
      image: "https://via.placeholder.com/400x500/4B0082/FFFFFF?text=Adire+Buba"
    },
    {
      id: '2',
      name: "Modern Adire T-Shirt",
      price: 8000,
      category: "unisex",
      description: "Contemporary Adire print t-shirt",
      image: "https://via.placeholder.com/400x500/000000/FFFFFF?text=Adire+T-Shirt"
    }
  ];
  
  res.json({
    success: true,
    count: products.length,
    products: products
  });
});

// ==================== START SERVER ====================
const PORT = 5000;
app.listen(PORT, () => {
  console.log('='.repeat(50));
  console.log('✅ REAL USER REGISTRATION SYSTEM');
  console.log('='.repeat(50));
  console.log(`📁 Database: ${DB_FILE}`);
  console.log(`👥 Users: ${usersDB.users.length} registered`);
  console.log(`🌐 Server: http://localhost:${PORT}`);
  console.log('='.repeat(50));
  console.log('🎉 Data is now SAVED to users.json file!');
  console.log('='.repeat(50));
});