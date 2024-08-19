import telebot
from config import TOKEN
from handlers import setup_handlers

bot = telebot.TeleBot(TOKEN, parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Buen día!👋 Soy el bot del Instituto Provincial de Estadística y Ciencia de Datos de la Provincia de Corrientes.")
    
    # Crear el menú de opciones
    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    board.add(
        telebot.types.KeyboardButton(text="IPICORR"),
        telebot.types.KeyboardButton(text="IPI"),
    )
    bot.send_message(message.chat.id, "¿En qué puedo ayudarte?", reply_markup=board)

# Configurar los manejadores adicionales
setup_handlers(bot)

# Iniciar la ejecución del bot
bot.polling()
