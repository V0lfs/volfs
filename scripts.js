// Инициализация корзины
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Функция добавления товара в корзину
function addToCart(name, price) {
    const item = { name, price };
    cart.push(item);
    localStorage.setItem('cart', JSON.stringify(cart));
    showNotification(`${name} добавлен в корзину!`);
}

// Функция отображения уведомления
function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Функция обновления корзины
function updateCart() {
    const cartItems = document.getElementById('cart-items');
    const totalElement = document.getElementById('total');

    if (!cartItems || !totalElement) return;

    cartItems.innerHTML = '';
    let total = 0;

    cart.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.innerHTML = `
            <span>${item.name} - ${item.price}₽</span>
            <button onclick="removeFromCart(${index})">Удалить</button>
        `;
        cartItems.appendChild(div);
        total += item.price;
    });

    totalElement.textContent = `${total}₽`;
}

// Функция удаления товара из корзины
function removeFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCart();
}

// Функция оформления заказа
function checkout() {
    if (cart.length === 0) {
        alert('Корзина пуста!');
        return;
    }
    alert('Спасибо за заказ! Мы свяжемся с вами.');
    cart = [];
    localStorage.removeItem('cart');
    updateCart();
}

// Обновление корзины при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    updateCart();
});
