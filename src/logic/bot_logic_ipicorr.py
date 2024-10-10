import sqlalchemy
import locale
import pandas as pd
import pymysql
import telebot
from helpers.bot_helpers import send_menu_principal
from datetime import datetime, timedelta
import unicodedata


# Variables globales para almacenar el dataframe y la fecha de carga
df_cache = None
last_load_time = None
CACHE_EXPIRATION_MINUTES = 30  # Duración del cache

def load_data():
    """Carga los datos si no están en caché o si el caché ha expirado."""
    global df_cache, last_load_time
    
    if df_cache is None or (last_load_time and (datetime.now() - last_load_time > timedelta(minutes=CACHE_EXPIRATION_MINUTES))):
        print("Cargando datos desde la base de datos...")
        engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/datalake_economico")
        df_cache = pd.read_sql_query("SELECT * FROM ipicorr", engine)
        
        # Multiplicamos las columnas por 100 para convertirlas a porcentaje
        columns_to_multiply = [
            'Var_Interanual_IPICORR', 
            'Var_Interanual_Alimentos', 
            'Var_Interanual_Textil', 
            'Var_Interanual_Maderas', 
            'Var_Interanual_MinNoMetalicos', 
            'Var_Interanual_Metales'
        ]
        df_cache[columns_to_multiply] = df_cache[columns_to_multiply] * 100
        last_load_time = datetime.now()  # Actualizamos el tiempo de la última carga
    else:
        print("Usando datos desde caché...")
    
    return df_cache

# Función para calcular la tendencia
def calcular_promedio_tendencia(df, meses):
    promedio = df['Var_Interanual_IPICORR'].iloc[-meses:].mean()
    if promedio > 0:
        return f"el índice IPICorr ha mostrado una tendencia al alza con un crecimiento promedio del {promedio:.2f}%"
    else:
        return f"el índice IPICorr ha mostrado una tendencia a la baja con un descenso promedio del {promedio:.2f}%"

# Función principal de respuesta sobre IPICORR (menú principal)
def resp_ipicorr(message, bot):
    df = load_data()
    user_input = message.text.lower().strip()

    if user_input == "¿que es?":
        bot.send_message(message.chat.id, "El Instituto Provincial de Estadistica y Ciencia de Datos en conjunto con el Ministerio de Industria, trabaja en el Índice de Producción Industrial manufacturero de la provincia de Corrientes (IPICorr). El mismo reúne información de las principales empresas industriales que producen y comercializan productos. Su objetivo es medir la evolución mensual de la actividad económica de la industria en la provincia.\n"
            "Las variaciones que tiene IPICORR son las siguientes:\n"
            "* Interanual IPICORR\n"
            "* Interanual Alimentos\n"
            "* Interanual Textil\n"
            "* Interanual Maderas\n"
            "* Interanual Minerales No Metalicos\n"
            "* Interanual Metales")        
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))  # Sigue en la misma función

    elif user_input == "ultimo valor":
        last_value = df['Var_Interanual_IPICORR'].iloc[-1]
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        fecha_texto = df['Fecha'].iloc[-1].strftime('%B %Y')
        bot.send_message(message.chat.id, f"El último valor de IPICORR es: {last_value :.2f}% correspondiente a {fecha_texto}")
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
            telebot.types.KeyboardButton(text="Volver al menú principal")
        )    
        bot.send_message(message.chat.id, "¿Qué variación te interesa consultar?", reply_markup=board)
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))
        
    elif user_input == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre IPICORR. ¿En qué más puedo ayudarte?")
        send_menu_principal(bot, message.chat.id)  # Envía el menú principal

    elif user_input == "¿cual es la tendencia de los ultimos meses?":
        board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="3 meses"),
            telebot.types.KeyboardButton(text="6 meses"),
            telebot.types.KeyboardButton(text="12 meses"),
            telebot.types.KeyboardButton(text="Quiero consultar otro tema de IPICORR"),
            telebot.types.KeyboardButton(text="Volver al menú principal")
        )
        bot.send_message(message.chat.id, "¿Sobre cuántos meses quieres ver la tendencia?", reply_markup=board)
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_tendencias(m, bot, df))

    else:
        bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))

# Función para gestionar las tendencias
def resp_ipicorr_tendencias(message, bot, df):
    user_input = message.text.lower().strip()

    if user_input in ["3 meses", "6 meses", "12 meses"]:
        meses = int(user_input.split()[0])
        respuesta = calcular_promedio_tendencia(df, meses)
        bot.send_message(message.chat.id, f"En los últimos {meses} meses, {respuesta}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_tendencias(m, bot, df))
        
    elif user_input == "quiero consultar otro tema de ipicorr":     
        hide_board = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Gracias por consultar sobre las variaciones de IPICORR", reply_markup=hide_board)
        send_menu_ipicorr(bot, message)
        
    elif user_input == "volver al menú principal":
        # Al seleccionar "Volver al menú principal", redirigir al menú principal (resp_ipicorr)
        bot.register_next_step_handler(message, lambda m: send_menu_ipicorr(bot, m))

    else:
        bot.send_message(message.chat.id, "Por favor selecciona una opción válida: '3 meses', '6 meses' o '12 meses'.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_tendencias(m, bot, df))


# Función para gestionar las variaciones
def resp_ipicorr_variaciones(message, bot, df):
    user_input = message.text.lower().strip()
    variaciones_mapping = {
        "interanual ipicorr": "Var_Interanual_IPICORR",
        "interanual alimentos": "Var_Interanual_Alimentos",
        "interanual textil": "Var_Interanual_Textil",
        "interanual maderas": "Var_Interanual_Maderas",
        "interanual minerales no metalicos": "Var_Interanual_MinNoMetalicos",
        "interanual metales": "Var_Interanual_Metales"
    }

    if user_input in variaciones_mapping:
        last_value = df[variaciones_mapping[user_input]].iloc[-1]
        fecha_texto = df['Fecha'].iloc[-1].strftime('%B %Y')
        bot.send_message(message.chat.id, f"El último valor de {user_input} es: {last_value :.2f}% correspondiente a {fecha_texto}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))
    
    elif user_input == "quiero consultar otro tema de ipicorr":     
        hide_board = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Gracias por consultar sobre las variaciones de IPICORR", reply_markup=hide_board)
        send_menu_ipicorr(bot, message)
    elif user_input == "volver al menú principal":
        hide_board = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Gracias por consultar sobre las variaciones de IPICORR", reply_markup=hide_board)
        send_menu_principal(bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))


def send_menu_ipicorr(bot, message):
    # Volver al menú inicial de IPICORR
    board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    board.add(
        telebot.types.KeyboardButton(text="¿Que es?"),
        telebot.types.KeyboardButton(text="Ultimo valor"),
        telebot.types.KeyboardButton(text="Variaciones"),
        telebot.types.KeyboardButton(text="¿Cual es la tendencia de los ultimos meses?"),
        telebot.types.KeyboardButton(text="Quiero saber de otro tema"),
    )

    bot.send_message(message.chat.id, "¿Qué tema quieres saber sobre IPICORR?", reply_markup=board)
    
    # Registrar el próximo paso para que resp_ipicorr maneje la respuesta del usuario
    bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))