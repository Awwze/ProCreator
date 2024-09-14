import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Определение состояний для ConversationHandler
LANGUAGE, MENU, GET_PROJECT_NAME, GET_DESCRIPTION, GET_NETWORK, GET_WALLET, GET_PHONE, FEEDBACK = range(8)

# Хранение данных пользователей
user_data = {}

# Доступные языки
languages = ["Русский", "English"]
lang_dict = {"Русский": "ru", "English": "en"}

# Тексты на разных языках
texts = {
    "start": {
        "ru": "Пожалуйста, выберите язык:",
        "en": "Please choose a language:"
    },
    "main_menu": {
        "ru": "Главное меню:",
        "en": "Main menu:"
    },
    "publish_project": {
        "ru": "Опубликовать проект",
        "en": "Publish a project"
    },
    "feedback": {
        "ru": "Оставить отзыв или пожелание",
        "en": "Leave feedback or wishes"
    },
    "project_name": {
        "ru": "Введите название проекта:",
        "en": "Enter the project name:"
    },
    "description": {
        "ru": "Введите ссылку на Telegraph с описанием проекта(создать можно на https://telegra.ph/) или небольшой текст:",
        "en": "Enter a link to Telegraph with a description of the project (you can create it at https://telegra.ph/) or a short text:"
    },
    "network": {
        "ru": "Введите сеть и название крипты (например, trc20/usdt):",
        "en": "Enter the network and crypto name (e.g., trc20/usdt):"
    },
    "wallet": {
        "ru": "Введите адрес кошелька:",
        "en": "Enter the wallet address:"
    },
    "phone": {
        "ru": "Пожалуйста, отправьте ваш номер телефона.",
        "en": "Please send your phone number."
    },
    "thank_you": {
        "ru": "Спасибо! Ваш проект опубликован.",
        "en": "Thank you! Your project has been published."
    },
    "choose_option": {
        "ru": "Пожалуйста, выберите один из пунктов меню.",
        "en": "Please choose one of the menu items."
    },
    "enter_feedback": {
        "ru": "Пожалуйста, напишите ваши пожелания и отзывы:",
        "en": "Please write your feedback and reviews:"
    },
    "feedback_thank_you": {
        "ru": "Спасибо за ваш отзыв!",
        "en": "Thank you for your feedback!"
    }
}

# Телеграм ID группы для уведомлений
admin_chat_id = -4111021752

# Начало общения
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [[language] for language in languages]
    await update.message.reply_text(
        texts['start']['ru'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return LANGUAGE

# Выбор языка
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id] = {'lang': lang_dict[update.message.text]}
    lang = user_data[user_id]['lang']
    await update.message.reply_text(
        texts['start'][lang],
        reply_markup=ReplyKeyboardRemove()
    )
    return await show_menu(update, context)

# Главное меню
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    lang = user_data[user_id]['lang']

    buttons = [
        [texts['publish_project'][lang], texts['feedback'][lang]]
    ]
    
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    
    await update.message.reply_text(
        texts['main_menu'][lang],
        reply_markup=reply_markup
    )
    
    return MENU

# Обработка выбора в главном меню
async def menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    text = update.message.text
    lang = user_data[user_id]['lang']
    
    if text == texts['publish_project'][lang]:
        await update.message.reply_text(texts['project_name'][lang], reply_markup=ReplyKeyboardRemove())
        return GET_PROJECT_NAME
    elif text == texts['feedback'][lang]:
        await update.message.reply_text(texts['enter_feedback'][lang], reply_markup=ReplyKeyboardRemove())
        return FEEDBACK
    else:
        await update.message.reply_text(texts['choose_option'][lang], reply_markup=ReplyKeyboardRemove())
        return MENU

# Публикация проекта: получение названия проекта
async def get_project_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['project_name'] = update.message.text
    lang = user_data[user_id]['lang']
    await update.message.reply_text(texts['description'][lang])
    return GET_DESCRIPTION

# Публикация проекта: получение описания проекта
async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['description'] = update.message.text
    lang = user_data[user_id]['lang']
    await update.message.reply_text(texts['network'][lang])
    return GET_NETWORK

# Публикация проекта: получение сети и названия крипты
async def get_network(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['network'] = update.message.text
    lang = user_data[user_id]['lang']
    await update.message.reply_text(texts['wallet'][lang])
    return GET_WALLET

# Публикация проекта: получение адреса кошелька
async def get_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['wallet'] = update.message.text
    lang = user_data[user_id]['lang']
    await update.message.reply_text(
        texts['phone'][lang],
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton(texts['phone'][lang], request_contact=True)]], one_time_keyboard=True, resize_keyboard=True)
    )
    return GET_PHONE

# Публикация проекта: получение номера телефона
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    user_data[user_id]['phone'] = update.message.contact.phone_number
    lang = user_data[user_id]['lang']
    user_info = user_data[user_id]
    user_name = update.message.from_user.username if update.message.from_user.username else "No username"

    await update.message.reply_text(
        texts['thank_you'][lang],
        reply_markup=ReplyKeyboardRemove()
    )

    message = (
        f"*Название:* {user_info['project_name']}\n\n"
        f"*Описание:*\n{user_info['description']}\n\n"
        f"*Сеть и крипта:* {user_info['network']}\n\n"
        f"*Адрес крипто-кошелька:* `{user_info['wallet']}`\n\n"
        f"*Номер телефона:* {user_info['phone']}\n\n"
        f"*Юзернейм:* @{user_name}"
    )

    await context.bot.send_message(
        chat_id=admin_chat_id,
        text=message,
        parse_mode='Markdown'
    )
    
    return await show_menu(update, context)

# Обработка отзывов и пожеланий
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    lang = user_data[user_id]['lang']
    user_name = update.message.from_user.username if update.message.from_user.username else "No username"

    message = (
        f"Новый отзыв от пользователя @{user_name}\n\n"
        f"{update.message.text}"
    )

    await context.bot.send_message(
        chat_id=admin_chat_id,
        text=message
    )

    await update.message.reply_text(texts['feedback_thank_you'][lang])
    
    return await show_menu(update, context)

# Отмена действий
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    lang = user_data[user_id]['lang']
    await update.message.reply_text(
        'Действие отменено.' if lang == 'ru' else 'Action cancelled.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Запуск бота
def run_bot():
    application = Application.builder().token("7298524057:AAHiEmhlPLfaDggZPW1w7i1BW5cequPmyIQ").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_selection)],
            GET_PROJECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_project_name)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            GET_NETWORK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_network)],
            GET_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wallet)],
            GET_PHONE: [MessageHandler(filters.CONTACT, get_phone)],
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    run_bot()
