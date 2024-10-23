# handlers.py
from logic.bot_logic_ipicorr import resp_ipicorr
from logic.bot_logic_ipi import resp_ipi_nacion
from logic.bot_logic_censo import resp_censo_departamento
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
    @bot.message_handler(func=lambda message: message.text in ["IPICORR", "IPI Nacion", "Censo"])
    def handle_choice(message):
        if message.text == "IPICORR":
            mostrar_menu_ipicorr(bot, message)
        elif message.text == "IPI Nacion":
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
            telebot.types.KeyboardButton(text="IPI Nacion"),
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
            telebot.types.KeyboardButton(text="¿Que es IPI Nacion?"),
            telebot.types.KeyboardButton(text="Ultimo valor"),
            telebot.types.KeyboardButton(text="Ver Grafico"),
            telebot.types.KeyboardButton(text="Consulta personalizada"),
            telebot.types.KeyboardButton(text="Comparar por fechas"),
            telebot.types.KeyboardButton(text="Quiero saber de otro tema"),
        )
        bot.send_message(message.chat.id, "¿Qué quieres saber sobre IPI?", reply_markup=board)
        bot.register_next_step_handler(message, partial(resp_ipi_nacion, bot=bot))

    # Menú de Censo
    def mostrar_menu_censo(bot, message):
        """Muestra el menú principal del censo con opciones claras y bien organizadas."""
        # Crear el teclado con opciones
        board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="Población Total en la Provincia"),
            telebot.types.KeyboardButton(text="Población por Municipio"),
            telebot.types.KeyboardButton(text="Variación de la Población"),
            telebot.types.KeyboardButton(text="Peso de la Población"),
            telebot.types.KeyboardButton(text="Quiero saber de otro tema")
        )

        # Formatear el mensaje del menú
        mensaje = (
            "📋 *Bienvenido a la sección de Censo 2022*\n\n"
            "🔎 Tenemos datos recolectados para la *provincia de Corrientes* "
            "con información detallada sobre municipios y departamentos.\n\n"
            "Selecciona una opción para obtener más información:\n"
            "🌍 *Población Total en la Provincia*: Consulta el total de habitantes en toda la provincia.\n"
            "👥 *Población por Municipio*: Consulta el número de habitantes por municipio.\n"
            "📈 *Variación de la Población*: Compara la población entre los censos de 2010 y 2022.\n"
            "⚖️ *Peso de la Población*: Muestra la proporción de cada municipio en la población total.\n"
            "\n🔙 *Quiero saber de otro tema*: Vuelve al menú principal."
        )

        # Enviar el mensaje del menú con el teclado
        bot.send_message(
            message.chat.id, 
            mensaje, 
            reply_markup=board, 
            parse_mode="Markdown"
        )
        # Registrar el siguiente paso para gestionar la respuesta del usuario
        bot.register_next_step_handler(message, partial(resp_censo_departamento, bot=bot))


