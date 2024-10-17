# handlers.py
from logic.bot_logic_ipicorr import resp_ipicorr
from logic.bot_logic_ipi import resp_ipi
from logic.bot_logic_censo import resp_censo
import telebot
from functools import partial

def setup_handlers(bot):
    # Manejador para saludos y mensajes iniciales
    @bot.message_handler(func=lambda message: message.text.lower() in ["hola", "buen día", "buenas", "qué tal", "buenas noches"])
    def handle_greetings(message):
        bot.reply_to(message, "¡Hola, buen día! 👋 Soy tu asistente del Instituto Provincial de Estadística y Ciencia de Datos 📊. ¿Qué datos o información estás buscando?")
        mostrar_menu_principal(bot, message)

    # Manejador para despedidas
    @bot.message_handler(func=lambda message: message.text.lower() in ["adiós", "adios", "gracias", "chau", "hasta luego", "nos vemos", "bye"])
    def handle_goodbye(message):
        bot.reply_to(message, "¡Hasta luego! 👋 Espero haberte sido de ayuda. No dudes en escribirme si necesitas más información.")

    # Manejador para opciones principales: IPICORR, IPI NACION, Censo
    @bot.message_handler(func=lambda message: message.text in ["IPICORR", "IPI NACION", "Censo"])
    def handle_choice(message):
        if message.text == "IPICORR":
            mostrar_menu_ipicorr(bot, message)
        elif message.text == "IPI NACION":
            mostrar_menu_ipi(bot, message)
        elif message.text == "Censo":
            mostrar_menu_censo(bot, message)

    # Manejador genérico para cualquier otra opción no válida
    @bot.message_handler(func=lambda message: True)
    def handle_invalid_option(message):
        bot.send_message(message.chat.id, "Opción no válida. Por favor, selecciona una opción del menú.")
        mostrar_menu_principal(bot, message)

    # Menú principal
    def mostrar_menu_principal(bot, message):
        board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="IPICORR"),
            telebot.types.KeyboardButton(text="IPI NACION"),
            telebot.types.KeyboardButton(text="Censo"),
        )
        bot.send_message(message.chat.id, "Selecciona una opción:", reply_markup=board)

    # Menú de IPICORR
    def mostrar_menu_ipicorr(bot, message):
        board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="¿Que es IPICORR?"),
            telebot.types.KeyboardButton(text="Ultimo valor"),
            telebot.types.KeyboardButton(text="Ver variaciones(categorias)"),
            telebot.types.KeyboardButton(text="¿Cual es la tendencia en los ultimos años?"),
            telebot.types.KeyboardButton(text="Ver grafico"),
            telebot.types.KeyboardButton(text="Consulta personalizada"),
            telebot.types.KeyboardButton(text="Quiero saber de otro tema")
        )
        bot.send_message(message.chat.id, "¿Qué quieres saber sobre IPICORR?", reply_markup=board)
        bot.register_next_step_handler(message, partial(resp_ipicorr, bot=bot))

    # Menú de IPI NACION
    def mostrar_menu_ipi(bot, message):
        board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="¿Que es?"),
            telebot.types.KeyboardButton(text="Quiero saber de otro tema"),
        )
        bot.send_message(message.chat.id, "¿Qué quieres saber sobre IPI?", reply_markup=board)
        bot.register_next_step_handler(message, partial(resp_ipi, bot=bot))

    # Menú de Censo
    def mostrar_menu_censo(bot, message):
        board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="Quiero saber mas"),
            telebot.types.KeyboardButton(text="Quiero saber de otro tema"),
        )
        bot.send_message(
            message.chat.id,
            "Como dato de Censo tenemos datos recolectados en 2022 para la provincia de Corrientes.",
            reply_markup=board
        )
        bot.register_next_step_handler(message, partial(resp_censo, bot=bot))
