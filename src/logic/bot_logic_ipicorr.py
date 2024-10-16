import sqlalchemy
import locale
import pandas as pd
import pymysql
import telebot
from helpers.bot_helpers import send_menu_principal
from datetime import datetime, timedelta

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
        df_cache['Fecha'] = pd.to_datetime(df_cache['Fecha'], format='%b-%Y')
        last_load_time = datetime.now()  # Actualizamos el tiempo de la última carga
    else:
        print("Usando datos desde caché...")
    
    return df_cache

# Función para calcular la tendencia por año
def calcular_promedio_anual(df, año):
    """Calcula el promedio de variaciones para un año completo."""
    datos_anuales = df[df['Fecha'].dt.year == año]

    if datos_anuales.empty:
        return f"No hay datos disponibles para el año {año}."

    promedio = datos_anuales['Var_Interanual_IPICORR'].mean()
    return f"El promedio de variación interanual en {año} fue de {promedio:.2f}%."

# Función principal de respuesta sobre IPICORR
def resp_ipicorr(message, bot):
    df = load_data()
    user_input = message.text.lower().strip()

    if user_input == "¿que es?":
        bot.send_message(message.chat.id, (
            "El IPICorr mide la evolución mensual de la industria en Corrientes. "
            "Incluye las siguientes variaciones:\n"
            "- Interanual IPICORR\n"
            "- Interanual Alimentos\n"
            "- Interanual Textil\n"
            "- Interanual Maderas\n"
            "- Interanual Minerales No Metálicos\n"
            "- Interanual Metales"
        ))
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))

    elif user_input == "ultimo valor":
        last_value = df['Var_Interanual_IPICORR'].iloc[-1]
        fecha = df['Fecha'].iloc[-1]
        fecha_texto = get_fecha_en_espanol(fecha)  # Usamos la nueva función

        bot.send_message(
            message.chat.id, 
            f"El último valor de IPICORR es: {last_value:.2f}% correspondiente a {fecha_texto}"
        )
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))

    elif user_input == "variaciones":
        mostrar_menu_variaciones(bot, message)

    elif user_input == "¿cual es la tendencia en los ultimos años?":
        mostrar_menu_tendencias(bot, message)

    elif user_input == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre IPICORR.")
        send_menu_principal(bot, message.chat.id)

    else:
        bot.send_message(message.chat.id, "Opción no válida. Elige nuevamente.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))

def mostrar_menu_variaciones(bot, message):
    """Muestra el menú de variaciones interanuales."""
    board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    opciones = [
        "Interanual IPICORR", "Interanual Alimentos", "Interanual Textil",
        "Interanual Maderas", "Interanual Minerales No Metalicos", 
        "Interanual Metales", "Volver al menú principal"
    ]
    for opcion in opciones:
        board.add(telebot.types.KeyboardButton(text=opcion))
    bot.send_message(message.chat.id, "¿Qué variación deseas consultar?", reply_markup=board)
    bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df_cache))

def mostrar_menu_tendencias(bot, message):
    """Muestra el menú para consultar tendencias por año."""
    board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    board.add(
        telebot.types.KeyboardButton(text="2022"),
        telebot.types.KeyboardButton(text="2023"),
        telebot.types.KeyboardButton(text="2024"),
        telebot.types.KeyboardButton(text="Volver al menú principal")
    )
    bot.send_message(message.chat.id, "¿De qué año deseas ver la tendencia?", reply_markup=board)
    bot.register_next_step_handler(message, lambda m: resp_ipicorr_tendencias(m, bot, df_cache))

def resp_ipicorr_tendencias(message, bot, df):
    """Responde con la tendencia anual para el año seleccionado."""
    user_input = message.text.strip()

    if user_input.isdigit() and int(user_input) in [2022, 2023, 2024]:
        año = int(user_input)
        respuesta = calcular_promedio_anual(df, año)
        bot.send_message(message.chat.id, respuesta)
        mostrar_menu_tendencias(bot, message)
    elif user_input == "volver al menú principal":
        send_menu_principal(bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Por favor selecciona un año válido.")
        mostrar_menu_tendencias(bot, message)

def resp_ipicorr_variaciones(message, bot, df):
    """Maneja las respuestas de variaciones."""
    user_input = message.text.lower().strip()
    variaciones = {
        "interanual ipicorr": "Var_Interanual_IPICORR",
        "interanual alimentos": "Var_Interanual_Alimentos",
        "interanual textil": "Var_Interanual_Textil",
        "interanual maderas": "Var_Interanual_Maderas",
        "interanual minerales no metalicos": "Var_Interanual_MinNoMetalicos",
        "interanual metales": "Var_Interanual_Metales"
    }

    if user_input in variaciones:
        last_value = df[variaciones[user_input]].iloc[-1]
        fecha_texto = df['Fecha'].iloc[-1].strftime('%B %Y')
        bot.send_message(message.chat.id, f"El último valor de {user_input} es: {last_value:.2f}% correspondiente a {fecha_texto}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))
    elif user_input == "volver al menú principal":
        send_menu_principal(bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Opción no válida. Elige nuevamente.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df))


def get_fecha_en_espanol(fecha):
    """Devuelve la fecha formateada en español."""
    try:
        # Intentamos establecer la localización a español
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        # Si no está disponible, intentamos con otra opción (Windows a veces usa 'Spanish_Spain')
        locale.setlocale(locale.LC_TIME, 'es_ES')

    # Formateamos la fecha al estilo "marzo 2024"
    fecha_en_espanol = fecha.strftime('%B %Y').capitalize()
    return fecha_en_espanol