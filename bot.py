import logging
import sqlite3
import telebot
from telebot import types

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Создание экземпляра бота
API_TOKEN = '7850122012:AAErxkP9TiQnqmSMQd-Ny4tk-aCf8GthijE'
bot = telebot.TeleBot(API_TOKEN)

# Функция для получения номеров из базы данных
def get_numbers():
    conn = sqlite3.connect('whatsapp_numbers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM numbers")
    numbers = cursor.fetchall()
    conn.close()
    return numbers

# Команда старт
@bot.message_handler(commands=['start'])
def start(message):
    text = "<b>Добро пожаловать!</b> \n\n|\n|\n|\nИспользуйте /list для просмотра доступных номеров. \n\n Обратиться в поддержку: @wababot_support_bot"
    image_path = 'img_start.png'  # Замените на путь к вашему изображению

    # Отправка изображения
    with open(image_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=text, parse_mode='HTML')

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
            text=f" +79********** Мессенджер - ({messenger}) - Цена - {price}₽",
            callback_data=phone_number
        )
        keyboard.add(button)

    bot.send_message(message.chat.id, "Выберите номер для аренды:", reply_markup=keyboard)

# Обработка нажатий кнопок
@bot.callback_query_handler(func=lambda call: True)
def button(call):
    # Здесь можно добавить логику для аренды номера (например, обработка платежей и т.д.)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text=f"Вы арендовали номер: {call.data}", chat_id=call.message.chat.id, message_id=call.message.message_id)

# Обработка неизвестных команд
@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    if not message.text.startswith('/'):
        bot.send_message(message.chat.id, "Неизвестная команда. Пожалуйста, используйте /start или /list.")

# Основная функция
if __name__ == '__main__':
    bot.polling(none_stop=True)
