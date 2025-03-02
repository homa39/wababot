import logging
import sqlite3
import telebot
from telebot import types
import time

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Создание экземпляра бота
API_TOKEN = '7850122012:AAErxkP9TiQnqmSMQd-Ny4tk-aCf8GthijE'  # Ваш реальный токен
CHAT_ID = '7369376817'  # Ваш реальный ID чата
bot = telebot.TeleBot(API_TOKEN)
user_data = {}
# Функция для получения номеров из базы данных
def get_numbers():
    conn = sqlite3.connect('whatsapp_numbers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM numbers")
    numbers = cursor.fetchall()
    conn.close()
    return numbers

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "<b>💻 Добро пожаловать!</b>\n\n"
        "Выберите действие:\n\n"
        "<i>Используйте кнопки ниже для навигации.</i> \n\n"
        "<i>Аренда номеров уже стала проще благодаря Waba, не теряйте драгоценное время ради лишения своих профитов.\n\nВведите /list для отображения каталога</i>\n\n"
    )

    # Создаем инлайн клавиатуру
    inline_keyboard = types.InlineKeyboardMarkup()
    support_button = types.InlineKeyboardButton(text="Тех. Поддержка", url="https://t.me/wababot_support_bot")
    inline_keyboard.add(support_button)

    # Создаем обычную клавиатуру
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_list = types.KeyboardButton("/list")
    keyboard.add(button_list)

    # Путь к изображению
    photo_path = 'Main_Png.png'  # Укажите путь к вашему изображению

    # Отправка изображения с текстом и инлайн кнопкой
    with open(photo_path, 'rb') as photo:
        bot.send_photo(chat_id=message.chat.id, photo=photo, caption=text, parse_mode='HTML', reply_markup=inline_keyboard)

image_path_katalog = 'Group_4.png'
# Команда для отображения списка номеров
@bot.message_handler(commands=['list'])
def list_numbers(message):
    numbers = get_numbers()
    if not numbers:
        bot.send_message(message.chat.id, "Нет доступных номеров.")
        return

    keyboard = types.InlineKeyboardMarkup()
    for number in numbers:
        phone_number, messenger, price = number[1], number[2], number[3]
        button = types.InlineKeyboardButton(
            text=f"+79********** Мессенджер - ({messenger}) - Цена - {price}₽",
            callback_data=f"rent_{phone_number}"
        )
        keyboard.add(button)

    back_button = types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    keyboard.add(back_button)

    #bot.send_message(message.chat.id, "Выберите номер для аренды:", reply_markup=keyboard)
    with open(image_path_katalog, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="Выберите номер для аренды:", reply_markup=keyboard)

# Обработка нажатий кнопок
@bot.callback_query_handler(func=lambda call: True)
def button(call):
    if call.data.startswith("rent_"):
        phone_number = call.data.split("_")[1]
        text = (
            "♻️ <b>Оплата банковской картой:</b>\n\n"
            "<i>Ваша заявка зарегистрирована</i>\n\n"
            "Реквизиты для оплаты банковской картой:\n"
            "└ <code>2200701753418570</code>\n\n\n"
            "Пожалуйста, отправьте скриншот квитанции о платеже."
        )

        # Путь к изображению
        photo_path = 'img_confirmation.png'  # Укажите путь к вашему изображению

        # Отправляем изображение с текстом
        with open(photo_path, 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo, caption=text, parse_mode='HTML')

        bot.answer_callback_query(call.id)

        # Устанавливаем состояние ожидания скриншота
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, handle_payment_confirmation)

    elif call.data == "back_to_menu":
        start(call.message)



 # Обработка скриншота квитанции
def handle_payment_confirmation(message):
    if message.content_type == 'photo':
        # Отправляем скриншот вам для проверки
        bot.send_photo(chat_id=CHAT_ID, photo=message.photo[-1].file_id,
                       caption=f"Квитанция от @{message.from_user.username} (ID: {message.from_user.id})")
        bot.send_message(message.chat.id, "Спасибо! Ваша квитанция принята. Ожидайте подтверждения.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте только скриншот квитанции о платеже.")


# Обработка неизвестных команд
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    if not message.text.startswith('/'):
        bot.send_message(message.chat.id, "Неизвестная команда. Пожалуйста, используйте /start или /list.")

# Основная функция
if __name__ == '__main__':
    bot.polling(none_stop=True)