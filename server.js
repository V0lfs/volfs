const express = require('express');
const mongoose = require('mongoose');
const app = express();

// Подключение к MongoDB
mongoose.connect('mongodb://localhost:27017/food-delivery', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// Схема заказа
const orderSchema = new mongoose.Schema({
    items: Array,
    total: Number,
    createdAt: { type: Date, default: Date.now }
});

const Order = mongoose.model('Order', orderSchema);

// Middleware
app.use(express.json());

// API для добавления заказа
app.post('/api/orders', async (req, res) => {
    const { items, total } = req.body;
    const order = new Order({ items, total });
    await order.save();
    res.status(201).json({ message: 'Заказ успешно создан!' });
});

// Запуск сервера
app.listen(3000, () => {
    console.log('Сервер запущен на порту 3000');
});
