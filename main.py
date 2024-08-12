import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

bot = telebot.TeleBot("6704512422:AAEtj7w5S0sIhyS0GyVzdFovEiICZQYrT4Q", parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Buen día!👋 Soy el bot del Instituto Provincial de Estadística y Ciencia de Datos de la Provincia de Corrientes. ¿En qué puedo ayudarte?")
    # Crear el menú de opciones
    board = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    board.add(
        KeyboardButton(text="Consultar estadísticas"),
        KeyboardButton(text="Contar palabras"),
        KeyboardButton(text="Contar caracteres"),
        KeyboardButton(text="Otras consultas")
    )

    # Enviar el menú al usuario
    bot.send_message(message.chat.id, "Por favor, elige una opción:", reply_markup=board)

@bot.message_handler(commands=['count'])
def count(message):
    board = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    board.add(
        KeyboardButton(text="contador de palabras"),
        KeyboardButton(text="contador de caracteres")
    )
    bot.send_message(message.chat.id, "¿Qué quieres contar?", reply_markup=board)
    bot.register_next_step_handler(message, handle_count_choice)

def handle_count_choice(message):
    if message.text.lower() == "contador de palabras":
        bot.send_message(message.chat.id, "Envía la frase para contar las palabras:")
        bot.register_next_step_handler(message, count_words)
    elif message.text.lower() == "contador de caracteres":
        bot.send_message(message.chat.id, "Envía la frase para contar los caracteres:")
        bot.register_next_step_handler(message, count_characters)
    else:
        bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
        count(message)  # Vuelve a mostrar el menú

def count_words(message):
    bot.send_message(message.chat.id, f"La frase tiene {len(message.text.split())} palabras.")

def count_characters(message):
    bot.send_message(message.chat.id, f"La frase tiene {len(message.text)} caracteres.")

bot.polling()
