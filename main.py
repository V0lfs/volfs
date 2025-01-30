from email.headerregistry import Address
from dadata import Dadata
import config
import logging
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# Цены
PRICES = {
    "Пицца Пепперони": types.LabeledPrice(label="Пицца Пепперони", amount=8000),  # 80 рублей
    "Пицца Маргарита": types.LabeledPrice(label="Пицца Маргарита", amount=7000),  # 70 рублей
    "Пицца Гавайская": types.LabeledPrice(label="Пицца Гавайская", amount=7500),  # 75 рублей
    "Кока-Кола": types.LabeledPrice(label="Кока-Кола", amount=1500),  # 15 рублей
    "Чизбургер": types.LabeledPrice(label="Чизбургер", amount=5000),  # 50 рублей
}

# Словарь для хранения состояния пользователей
user_states = {}
# Словарь для хранения идентификаторов сообщений
messages_to_delete = {}

# Главное меню
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
main_keyboard.add(
    KeyboardButton("Меню"), KeyboardButton("Корзина"),
    KeyboardButton("О нас"), KeyboardButton("Контакты"),
    KeyboardButton("Поддержка"), KeyboardButton("Отзыв"),
    KeyboardButton("История заказов (В разработке)"),
    KeyboardButton("Статус заказа (В разработке)")
)

# Меню с продуктами
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
menu_keyboard.add(
    KeyboardButton("Пицца Пепперони"), KeyboardButton("Пицца Маргарита"),
    KeyboardButton("Пицца Гавайская"), KeyboardButton("Кока-Кола"),
    KeyboardButton("Чизбургер"), KeyboardButton("Корзина"),
    KeyboardButton("Назад")
)

# Клавиатура с кнопкой "Назад"
back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Назад"))

# Функция для проверки адреса
def is_valid_address(address):
    pattern = r'Екатеринбург.*'
    return re.match(pattern, address, re.IGNORECASE) is not None

# Проверка номера телефона
def is_valid_phone(phone):
    return re.match(r'^\+7\d{10}$|^8\d{10}$', phone) is not None and len(phone) in [11, 12]

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_states[message.chat.id] = {"step": 0, "cart": {}, "address": None, "phone": None, "comment": None}
    await message.answer("👋 Привет! Добро пожаловать в нашу пиццерию! 🎉\n\nВыберите действие:", reply_markup=main_keyboard)

# Обработчик кнопки "Статус заказа"
@dp.message_handler(lambda message: message.text == "Статус заказа (В разработке)")
async def about_command(message: types.Message):
    about_text = (
        "Данный раздел пока что находится в разработке. \nВернитесь в главное меню."
    )
    await message.answer(about_text, reply_markup=back_keyboard)

# Обработчик кнопки "Меню"
@dp.message_handler(lambda message: message.text == "Меню")
async def show_menu(message: types.Message):
    await message.answer("Выберите продукт:", reply_markup=menu_keyboard)

# Обработчик кнопки "О нас"
@dp.message_handler(lambda message: message.text == "О нас")
async def about_command(message: types.Message):
    about_text = (
        "🍕 Добро пожаловать в нашу пиццерию!\n\n"
        "Мы предлагаем самые вкусные пиццы и напитки. Закажите прямо сейчас и наслаждайтесь!"
    )
    await message.answer(about_text, reply_markup=back_keyboard)

# Обработчик кнопки "Контакты"
@dp.message_handler(lambda message: message.text == "Контакты")
async def contact_command(message: types.Message):
    await message.answer("Наш телефон: +7 (996) 186-89-91\nНаш тг: @volfs_volfs", reply_markup=back_keyboard)

# Обработчик кнопки "Поддержка"
@dp.message_handler(lambda message: message.text == "Поддержка")
async def support_command(message: types.Message):
    await message.answer("Если у вас возникли проблемы, напишите нам на @volfs_volfs.", reply_markup=back_keyboard)

# Обработчик кнопки "Отзыв"
@dp.message_handler(lambda message: message.text == "Отзыв")
async def feedback_command(message: types.Message):
    if message.chat.id not in user_states:
        user_states[message.chat.id] = {"step": 0, "cart": {}, "address": None, "phone": None, "comment": None}

    await message.answer("Пожалуйста, напишите ваш отзыв или предложение:", reply_markup=back_keyboard)
    user_states[message.chat.id]["waiting_for_feedback"] = True

# Обработчик ввода отзыва
@dp.message_handler(lambda message: message.chat.id in user_states and user_states[message.chat.id].get("waiting_for_feedback", False))
async def process_feedback(message: types.Message):
    if message.text == "Назад":
        await message.answer("Вы вернулись в главное меню. Выберите действие:", reply_markup=main_keyboard)
        user_states[message.chat.id]["waiting_for_feedback"] = False
        return

    feedback = message.text
    await bot.send_message(config.CHAT, f"Новый отзыв от {message.from_user.full_name}:\n{feedback}")
    await message.answer("Спасибо за ваш отзыв!", reply_markup=main_keyboard)
    user_states[message.chat.id]["waiting_for_feedback"] = False

# Обработчик кнопки "История заказов"
@dp.message_handler(lambda message: message.text == "История заказов (В разработке)")
async def order_history(message: types.Message):
    await message.answer("Ваша история заказов пока недоступна.", reply_markup=back_keyboard)

# Обработчик кнопки "Назад"
@dp.message_handler(lambda message: message.text == "Назад")
async def handle_back(message: types.Message):
    chat_id = message.chat.id
    if chat_id in user_states:
        step = user_states[chat_id].get("step", 0)
        if step == 1:  # Если пользователь вводил адрес
            await message.answer("Вы вернулись к выбору продуктов. Выберите продукт:", reply_markup=menu_keyboard)
            user_states[chat_id]["step"] = 0
        elif step == 2:  # Если пользователь вводил телефон
            await message.answer("Пожалуйста, введите ваш полный адрес (пример: Екатеринбург, ул 8 марта 12, 2 подъезд, кв 48):", reply_markup=back_keyboard)
            user_states[chat_id]["step"] = 1
        elif step == 3:  # Если пользователь подтверждал заказ
            await message.answer("Пожалуйста, введите ваш номер телефона (пример: +79012345678 или 89012345678):", reply_markup=back_keyboard)
            user_states[chat_id]["step"] = 2
        elif step == 4:  # Если пользователь вводил комментарий
            await message.answer("Желаете добавить комментарии к заказу?):", reply_markup=back_keyboard)
            user_states[chat_id]["step"] = 3
        else:
            await message.answer("Вы вернулись в главное меню. Выберите действие:", reply_markup=main_keyboard)
    else:
        await message.answer("Вы вернулись в главное меню. Выберите действие:", reply_markup=main_keyboard)

# Обработчик выбора продукта
@dp.message_handler(lambda message: message.text in PRICES.keys())
async def process_product_order(message: types.Message):
    if message.chat.id not in user_states:
        user_states[message.chat.id] = {"step": 0, "cart": {}, "address": None, "phone": None, "comment": None}
        
    product = message.text
    user_states[message.chat.id]["cart"][product] = user_states[message.chat.id]["cart"].get(product, 0) + 1
    await message.answer(f"Вы добавили {product} в корзину. Чтобы продолжить, выберите другой продукт или посмотрите корзину.", reply_markup=menu_keyboard)

# Обработчик кнопки "Корзина"
@dp.message_handler(lambda message: message.text == "Корзина" and message.chat.id in user_states)
async def view_cart(message: types.Message):
    cart = user_states[message.chat.id]["cart"]
    if not cart:
        await message.answer("Ваша корзина пуста. Выберите продукты, чтобы добавить их в корзину.", reply_markup=back_keyboard)
        return

    cart_message = "Ваша корзина:\n"
    total_amount = 0
    for product, quantity in cart.items():
        price = PRICES[product].amount / 100  # Приводим к рублям
        cart_message += f"{product} - {quantity} шт. по {price} рублей\n"
        total_amount += price * quantity

    cart_message += f"\nИтого: {total_amount} рублей\n\nХотите оформить заказ или очистить корзину?"
    await message.answer(cart_message, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Оформить заказ"), KeyboardButton("Очистить корзину"), KeyboardButton("Назад")))

# Обработчик кнопки "Очистить корзину"
@dp.message_handler(lambda message: message.text == "Очистить корзину" and message.chat.id in user_states)
async def clear_cart_confirmation(message: types.Message):
    await message.answer("Вы уверены, что хотите очистить корзину?", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Да"), KeyboardButton("Нет")))

# Обработчик подтверждения очистки корзины
@dp.message_handler(lambda message: message.text == "Да" and message.chat.id in user_states)
async def clear_cart(message: types.Message):
    user_states[message.chat.id]["cart"] = {}
    await message.answer("Ваша корзина очищена. Выберите продукты, чтобы добавить их в корзину.", reply_markup=main_keyboard)

# Обработчик отмены очистки корзины
@dp.message_handler(lambda message: message.text == "Нет" and message.chat.id in user_states)
async def cancel_clear_cart(message: types.Message):
    await message.answer("Очистка корзины отменена.", reply_markup=main_keyboard)

# Обработчик кнопки "Оформить заказ"
@dp.message_handler(lambda message: message.text == "Оформить заказ" and message.chat.id in user_states)
async def initiate_order(message: types.Message):
    cart = user_states[message.chat.id]["cart"]
    if not cart:
        await message.answer("Ваша корзина пуста. Добавьте продукты в корзину, прежде чем оформлять заказ.", reply_markup=main_keyboard)
        return

    user_states[message.chat.id]["step"] = 1
    await message.answer("Пожалуйста, введите ваш полный адрес (пример: Екатеринбург, ул 8 марта 12, 2 подъезд, кв 48):", reply_markup=back_keyboard)

# Обработчик ввода адреса
@dp.message_handler(lambda message: message.chat.id in user_states and user_states[message.chat.id]["step"] == 1)
async def get_address(message: types.Message):
    if message.text == "Назад":
        await message.answer("Вы вернулись к выбору продуктов. Выберите продукт:", reply_markup=menu_keyboard)
        user_states[message.chat.id]["step"] = 0
        return
    
    address = message.text
    if not is_valid_address(address):
        await message.answer("Пожалуйста, введите корректный адрес в Екатеринбурге (пример: Екатеринбург, ул 8 марта 12, 2 подъезд, кв 48):")
        return

    user_states[message.chat.id]["address"] = address
    user_states[message.chat.id]["step"] = 2
    await message.answer("Пожалуйста, введите ваш номер телефона (пример: +79012345678 или 89012345678):", reply_markup=back_keyboard)


# Обработчик ввода номера телефона
@dp.message_handler(lambda message: message.chat.id in user_states and user_states[message.chat.id]["step"] == 2)
async def get_phone(message: types.Message):
    if message.text == "Назад":
        await message.answer("Пожалуйста, введите ваш полный адрес (пример: Екатеринбург, ул 8 марта 12, 2 подъезд, кв 48):", reply_markup=back_keyboard)
        user_states[message.chat.id]["step"] = 1
        return

    phone = message.text
    if not is_valid_phone(phone):
        await message.answer("Номер телефона неправильный. Пожалуйста, введите ваш номер телефона (пример: +79012345678 или 89012345678):", reply_markup=back_keyboard)
        return

    user_states[message.chat.id]["phone"] = phone
    user_states[message.chat.id]["step"] = 3
    await message.answer("Желаете добавить комментарии к заказу?", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Пропустить"), KeyboardButton("Назад")))

# Обработчик ввода комментария
@dp.message_handler(lambda message: message.chat.id in user_states and user_states[message.chat.id]["step"] == 3)
async def get_comment(message: types.Message):
    if message.text == "Назад":
        await message.answer("Пожалуйста, введите ваш номер телефона (пример: +79012345678 или 89012345678):", reply_markup=back_keyboard)
        user_states[message.chat.id]["step"] = 2
        return

    if message.text == "Пропустить":
        user_states[message.chat.id]["comment"] = None
    else:
        user_states[message.chat.id]["comment"] = message.text

    user_states[message.chat.id]["step"] = 4
    address = user_states[message.chat.id]["address"]
    phone = user_states[message.chat.id]["phone"]
    comment = user_states[message.chat.id]["comment"]
    cart_message = format_cart(user_states[message.chat.id]["cart"])
    
    order_message = f"Ваш заказ:\n{cart_message}\nАдрес: {address}\nНомер телефона: {phone}\n"
    if comment:
        order_message += f"Комментарий: {comment}\n"
    
    order_message += "\nХотите оплатить?"
    
    await message.answer(
        order_message,
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Оплатить"), KeyboardButton("Отмена"), KeyboardButton("Назад"))
    )

# Функция для форматирования корзины
def format_cart(cart):
    cart_message = ""
    for product, quantity in cart.items():
        price = PRICES[product].amount / 100  # Приводим к рублям
        cart_message += f"{product} - {quantity} шт. по {price} рублей\n"
    return cart_message

# Обработчик подтверждения заказа
@dp.message_handler(lambda message: message.chat.id in user_states and user_states[message.chat.id]["step"] == 4)
async def confirm_order(message: types.Message):
    if message.text == "Оплатить":
        await initiate_payment(message)
    elif message.text == "Назад":
        await message.answer("Желаете добавить комментарии к заказу?", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Пропустить"), KeyboardButton("Назад")))
        user_states[message.chat.id]["step"] = 3
    elif message.text == "Отмена":
        await cancel_order(message)

# Обработчик отмены заказа
@dp.message_handler(lambda message: message.text == "Отмена" and message.chat.id in user_states)
async def cancel_order(message: types.Message):
    chat_id = message.chat.id
    if chat_id in user_states:
        del user_states[chat_id]
    await message.answer("Ваш заказ отменен. Вы вернулись в главное меню. Выберите действие:", reply_markup=main_keyboard)

# Обработчик инициализации оплаты
@dp.message_handler(lambda message: message.text == "Оплатить" and message.chat.id in user_states and user_states[message.chat.id]["step"] == 4)
async def initiate_payment(message: types.Message):
    cart = user_states[message.chat.id]["cart"]
    total_amount = sum(PRICES[product].amount * quantity for product, quantity in cart.items())
    if total_amount == 0:
        await message.answer("Произошла ошибка. Ваша корзина пуста.")
        return

    await buy_pizza(message.chat.id, types.LabeledPrice(label="Ваш заказ", amount=total_amount))

# Функция для отправки счета на оплату
async def buy_pizza(chat_id, price):
    try:
        bot_message = await bot.send_invoice(chat_id, 
                            title="Ваш заказ",
                            description="Оплата за ваш заказ.",
                            provider_token=config.PAYMENTS_TOKEN,
                            currency="rub",
                            is_flexible=False,
                            prices=[price],
                            start_parameter="pizza-order",
                            payload="pizza-order-payload")
        
        if chat_id not in messages_to_delete:
            messages_to_delete[chat_id] = []   
        messages_to_delete[chat_id].append(bot_message.message_id)

        await bot.send_message(chat_id, "Вы снова находитесь в главном меню. В поле 'Статус заказа' вы можете посмотреть статус вашего заказа", reply_markup=back_keyboard)

    except Exception as e:
        logging.error(f"Ошибка при отправке счета на оплату: {e}")
        await bot.send_message(chat_id, "Произошла ошибка при отправке счета на оплату.")

# Обработчик предоплаты
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Обработчик успешного платежа
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    logging.info("Обработчик успешного платежа вызван.")
    
    developer_message = (
        f"Пользователь {message.from_user.full_name} успешно оплатил заказ:\n"
        f"Сумма: {message.successful_payment.total_amount / 100} рублей\n"
        f"Заказ:\n{format_cart(user_states[message.chat.id]['cart'])}\n"
        f"Адрес: {user_states[message.chat.id]['address']}\n"
        f"Номер телефона: {user_states[message.chat.id]['phone']}\n"
    )
    
    if user_states[message.chat.id]["comment"]:
        developer_message += f"Комментарий: {user_states[message.chat.id]['comment']}\n"
    
    # Отправка сообщения пользователю о успешной оплате
    await message.answer("Спасибо за ваш заказ! 🎉\nВаш заказ будет доставлен на указанный адрес.")
    
    logging.info(developer_message)

    try:
        await bot.send_message(config.DEVELOPER_CHAT_ID, developer_message)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения разработчику: {e}")
    
    if message.chat.id in messages_to_delete:
        for msg_id in messages_to_delete[message.chat.id]:
            try:
                await bot.delete_message(message.chat.id, msg_id)
            except Exception as e:
                logging.error(f"Ошибка при удалении сообщения: {e}")
        del messages_to_delete[message.chat.id]
    
    # Устанавливаем состояние для возврата к выбору продуктов
    user_states[message.chat.id]["step"] = 0  # Возвращаемся к выбору продуктов
    user_states[message.chat.id]["cart"] = {}  # Очищаем корзину
    user_states[message.chat.id]["comment"] = None  # Очищаем комментарий
    # Добавляем кнопку "Назад"
    await message.answer("Вы вернулись в главное меню. Отслеживайте заказ во вкладке 'Статус заказа'.", reply_markup=main_keyboard)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
