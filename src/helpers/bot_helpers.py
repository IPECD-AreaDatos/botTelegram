# bot_helpers.py
import telebot

def send_menu_principal(bot, chat_id):
    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    board.add(
        telebot.types.KeyboardButton(text="IPICORR"),
        telebot.types.KeyboardButton(text="IPI Nacion"),
        telebot.types.KeyboardButton(text="Censo"),
    )
    bot.send_message(chat_id, "¿En qué puedo ayudarte?", reply_markup=board)