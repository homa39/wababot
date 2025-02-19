from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import time

# Ваш токен бота техподдержки
SUPPORT_BOT_TOKEN = '8012237386:AAHmnXAKq3YOM4f8hVL-ncmkwomJAHuRYxc'
SUPPORT_CHAT_ID = '7369376817'

# Словарь для хранения времени последнего обращения пользователей
user_last_contact_time = {}

# Время ожидания между обращениями (в секундах)
TIME_LIMIT = 30 * 60  # 30 минут

# Функция для старта диалога
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Добро пожаловать в техподдержку! Пожалуйста, напишите ваше сообщение.')

# Получение сообщения от пользователя и отправка в техподдержку
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text
    user_name = update.message.from_user.username or update.message.from_user.first_name

    current_time = time.time()

    # Проверяем, есть ли у пользователя запись о последнем обращении
    last_contact_time = user_last_contact_time.get(user_id)

    # Если запись есть и время с последнего обращения меньше 30 минут
    if last_contact_time and (current_time - last_contact_time < TIME_LIMIT):
        remaining_time = TIME_LIMIT - (current_time - last_contact_time)
        await update.message.reply_text(f'Вы не можете обращаться в поддержку так часто. Пожалуйста, подождите еще {int(remaining_time // 60)} минут и {int(remaining_time % 60)} секунд.')
        return

    # Отправка сообщения в техподдержку
    await context.bot.send_message(chat_id=SUPPORT_CHAT_ID, text=f"Сообщение от @{user_name} (ID: {user_id}):\n{user_message}")

    # Обновляем время последнего обращения пользователя
    user_last_contact_time[user_id] = current_time
    
    await update.message.reply_text("Ваше сообщение отправлено в техподдержку. Мы свяжемся с вами скоро.")

def main() -> None:
    app = ApplicationBuilder().token(SUPPORT_BOT_TOKEN).build()

    # Определяем обработчики команд и сообщений
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    app.run_polling()

if __name__ == '__main__':
    main()
