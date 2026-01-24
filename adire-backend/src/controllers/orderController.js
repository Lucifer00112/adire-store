const Order = require('../models/Order');
const Product = require('../models/Product');

exports.createOrder = async (req, res) => {
  try {
    // Get order details from customer
    const { items, shippingAddress, paymentMethod } = req.body;
    
    // Calculate total price
    let subtotal = 0;
    for (const item of items) {
      const product = await Product.findById(item.product);
      subtotal += product.price * item.quantity;
    }
    
    // Add shipping cost
    const shippingFee = 1500; // 1500 NGN for Nigeria
    const total = subtotal + shippingFee;
    
    // Save the order to database
    const order = await Order.create({
      user: req.user._id,
      items,
      shippingAddress,
      paymentMethod,
      subtotal,
      shippingFee,
      total
    });
    
    res.status(201).json({
      message: 'Order created successfully',
      order
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};