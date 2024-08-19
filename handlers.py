from ipicorr import resp_ipicorr
import telebot
from functools import partial

def setup_handlers(bot):
    @bot.message_handler(func=lambda message: message.text in ["IPICORR"])
    def handle_choice(message):
        if message.text == "IPICORR":
            bot.send_message(message.chat.id, "¿Qué quieres saber?")
            
            # Creación del teclado (keyboard) de opciones
            board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            board.add(
                telebot.types.KeyboardButton(text="Que es?"),
                telebot.types.KeyboardButton(text="Ultimo valor"),
            )
            
            bot.send_message(message.chat.id, "Selecciona una opción:", reply_markup=board)
            bot.register_next_step_handler(message, partial(resp_ipicorr, bot=bot))
        else:
            bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
