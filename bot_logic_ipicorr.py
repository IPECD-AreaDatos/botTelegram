import sqlalchemy
import pandas as pd
import pymysql
import telebot
from bot_helpers import send_menu_principal

def read_data():
    engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/datalake_economico")
    df = pd.read_sql_query("SELECT * FROM ipicorr", engine)
    print(df)
    columns_to_multiply = [
        'Var_Interanual_IPICORR', 
        'Var_Interanual_Alimentos', 
        'Var_Interanual_Textil', 
        'Var_Interanual_Maderas', 
        'Var_Interanual_MinNoMetalicos', 
        'Var_Interanual_Metales'
    ]

    df[columns_to_multiply] = df[columns_to_multiply] * 100

    return df

def resp_ipicorr(message, bot):
    df = read_data()
    user_input = message.text.lower()

    if user_input == "¿que es?":
        bot.send_message(message.chat.id, "El Instituto Provincial de Estadistica y Ciencia de Datos en conjunto con el Ministerio de Industria, trabaja en el Índice de Producción Industrial manufacturero de la provincia de Corrientes (IPICorr). El mismo reúne información de las principales empresas industriales que producen y comercializan productos. Su objetivo es medir la evolución mensual de la actividad económica de la industria en la provincia.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))  # Mantiene al usuario en la misma función
        
    elif user_input == "ultimo valor":
        last_value = df['Var_Interanual_IPICORR'].iloc[-1]
        bot.send_message(message.chat.id, f"El ultimo valor de IPICORR es: {last_value :.2f}% correspondiente a {df['Fecha'].iloc[-1]}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))

    elif user_input == "variaciones":
        board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="Interanual IPICORR"),
            telebot.types.KeyboardButton(text="Interanual Alimentos"),
            telebot.types.KeyboardButton(text="Interanual Textil"),
            telebot.types.KeyboardButton(text="Interanual Maderas"),
            telebot.types.KeyboardButton(text="Interanual Minerales No Metalicos"),
            telebot.types.KeyboardButton(text="Interanual Metales"),
            telebot.types.KeyboardButton(text="Quiero consultar otro tema de IPICORR"),
        )    
        bot.send_message(message.chat.id, "¿Que Variacion te interesa consultar?", reply_markup=board)
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))

    elif user_input == "¿que variaciones tiene?":
        bot.send_message(message.chat.id, 
            "Las variaciones que tiene IPICORR son las siguientes:\n"
            "* Interanual IPICORR\n"
            "* Interanual Alimentos\n"
            "* Interanual Textil\n"
            "* Interanual Maderas\n"
            "* Interanual Minerales No Metalicos\n"
            "* Interanual Metales")

        
    elif user_input == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre IPICORR. ¿En qué más puedo ayudarte?")
        send_menu_principal(bot, message.chat.id)  # Usar la función para enviar el menú principal

        
    else:
        bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot)) 


def resp_ipicorr_variaciones(message, bot, df):
    user_input = message.text.lower().strip()

    if user_input == "interanual ipicorr":
        last_value = df['Var_Interanual_IPICORR'].iloc[-1]
        bot.send_message(message.chat.id, f"El último valor de IPICORR es: {last_value :.2f}% correspondiente a {df['Fecha'].iloc[-1]}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))

    elif user_input == "interanual alimentos":
        last_value = df['Var_Interanual_Alimentos'].iloc[-1]
        bot.send_message(message.chat.id, f"El último valor de alimentos de IPICORR es: {last_value :.2f}% correspondiente a {df['Fecha'].iloc[-1]}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))

    elif user_input == "interanual textil":
        last_value = df['Var_Interanual_Textil'].iloc[-1]
        bot.send_message(message.chat.id, f"El último valor de textil de IPICORR es: {last_value :.2f}% correspondiente a {df['Fecha'].iloc[-1]}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))

    elif user_input == "interanual maderas":
        last_value = df['Var_Interanual_Maderas'].iloc[-1]
        bot.send_message(message.chat.id, f"El último valor de maderas de IPICORR es: {last_value :.2f}% correspondiente a {df['Fecha'].iloc[-1]}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))

    elif user_input == "interanual minerales no metalicos":
        last_value = df['Var_Interanual_MinNoMetalicos'].iloc[-1]
        bot.send_message(message.chat.id, f"El último valor de minerales no metálicos de IPICORR es: {last_value :.2f}% correspondiente a {df['Fecha'].iloc[-1]}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))

    elif user_input == "interanual metales":
        last_value = df['Var_Interanual_Metales'].iloc[-1]
        bot.send_message(message.chat.id, f"El último valor de metales de IPICORR es: {last_value :.2f}% correspondiente a {df['Fecha'].iloc[-1]}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))

    elif user_input == "quiero consultar otro tema de ipicorr":     
        # Restablecer el teclado con opciones vacías para asegurarse de que se actualice correctamente
        hide_board = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Gracias por consultar sobre las variaciones de IPICORR", reply_markup=hide_board)

        # Volver al menú inicial de IPICORR
        board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="¿Que es?"),
            telebot.types.KeyboardButton(text="Ultimo valor"),
            telebot.types.KeyboardButton(text="¿Que variaciones tiene?"),
            telebot.types.KeyboardButton(text="Variaciones"),
            telebot.types.KeyboardButton(text="Quiero saber de otro tema"),
        )

        bot.send_message(message.chat.id, "¿Qué tema quieres saber sobre IPICORR?", reply_markup=board)
        
        # Registrar el próximo paso para que resp_ipicorr maneje la respuesta del usuario
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))
    
    else:
        bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))
