# handlers.py
from bot_logic_ipicorr import resp_ipicorr
from bot_logic_ipi import resp_ipi
import telebot
from functools import partial

def setup_handlers(bot):
    @bot.message_handler(func=lambda message: message.text in ["IPICORR", "IPI"])
    def handle_choice(message):
        if message.text == "IPICORR":
            board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            board.add(
                telebot.types.KeyboardButton(text="¿Que es?"),
                telebot.types.KeyboardButton(text="Ultimo valor"),
                telebot.types.KeyboardButton(text="Variaciones"),
                telebot.types.KeyboardButton(text="Quiero saber de otro tema"),
            )
            bot.send_message(message.chat.id, "¿Qué quieres saber sobre IPICORR?", reply_markup=board)
            bot.register_next_step_handler(message, partial(resp_ipicorr, bot=bot))
        elif message.text == "IPI Nacion":
            board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            board.add(
                telebot.types.KeyboardButton(text="¿Que es?"),
                telebot.types.KeyboardButton(text="Quiero saber de otro tema"),
            )
            bot.send_message(message.chat.id, "¿Qué quieres saber sobre IPI?", reply_markup=board)
            bot.register_next_step_handler(message, partial(resp_ipi, bot=bot))
        else:
            bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
