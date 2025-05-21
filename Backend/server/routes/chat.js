const express = require('express');
const router = express.Router();
const chatController = require('../controllers/chatController');

router.post('/recommend', chatController.recommend);

module.exports = router;
