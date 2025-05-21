const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();

const userRoutes = require('./routes/users');
const planRoutes = require('./routes/plans');
const chatRoutes = require('./routes/chat');
const googlePlacesRoutes = require('./routes/googlePlacesRoutes');

app.use('/api/chat', chatRoutes);

app.use(cors());
app.use(express.json());

app.use('/api/users', userRoutes);
app.use('/api/plans', planRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/google-places', googlePlacesRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));