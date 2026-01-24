// Simple auth middleware for now (will replace with real JWT)
const auth = (req, res, next) => {
  // For now, create a dummy user
  req.user = {
    _id: 'user_' + Date.now(),
    role: 'customer'
  };
  
  next();
};

const adminAuth = (req, res, next) => {
  auth(req, res, () => {
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required' });
    }
    next();
  });
};

module.exports = { auth, adminAuth };