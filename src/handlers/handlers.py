# handlers.py
from logic.bot_logic_ipicorr import resp_ipicorr
from logic.bot_logic_ipi import resp_ipi
from logic.bot_logic_censo import resp_censo
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
                telebot.types.KeyboardButton(text="¿Cual es la tendencia de los ultimos meses?"),
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
        elif message.text == "Censo":
            bot.send_message(message.chat.id, "Como dato de Censo tenemos datos recolectados en 2022 para la provincia de Corrientes. Eliga de que forma quiere verlos:")
            board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            board.add(
                telebot.types.KeyboardButton(text="Departamentos"),
                telebot.types.KeyboardButton(text="Municipios"),
            )
            bot.register_next_step_handler(message, partial(resp_censo, bot=bot))
        else:
            bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
