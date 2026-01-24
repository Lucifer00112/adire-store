const express = require('express');
const router = express.Router();
const orderController = require('../controllers/orderController');
const { auth } = require('../middleware/auth');

router.post('/', auth, orderController.createOrder);       // Create new order
router.get('/', auth, orderController.getUserOrders);      // Get my orders
router.get('/:id', auth, orderController.getOrderById);    // Get order details

module.exports = router;