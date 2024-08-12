def setup_handlers(bot):
    @bot.message_handler(func=lambda message: message.text in ["Contar palabras", "Contar caracteres"])
    def handle_count_choice(message):
        if message.text == "Contar palabras":
            bot.send_message(message.chat.id, "Envía la frase para contar las palabras:")
            bot.register_next_step_handler(message, count_words)
        elif message.text == "Contar caracteres":
            bot.send_message(message.chat.id, "Envía la frase para contar los caracteres:")
            bot.register_next_step_handler(message, count_characters)
        else:
            bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")

    def count_words(message):
        bot.send_message(message.chat.id, f"La frase tiene {len(message.text.split())} palabras.")

    def count_characters(message):
        bot.send_message(message.chat.id, f"La frase tiene {len(message.text)} caracteres.")
