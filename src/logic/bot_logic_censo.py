import sqlalchemy
import locale
import pandas as pd
import pymysql
import telebot
from helpers.bot_helpers import send_menu_principal
from datetime import datetime, timedelta
import unicodedata
from functools import partial
import locale
df_cache_departamentos = None
df_cache_municipios = None
last_load_time_departamentos = None
last_load_time_municipios = None
CACHE_EXPIRATION_MINUTES = 30

# ----------------- Funciones de Cache -----------------
def read_data_censo_departamentos():
    """Carga los datos de departamentos desde la base de datos o desde caché."""
    global df_cache_departamentos, last_load_time_departamentos
    if df_cache_departamentos is None or (last_load_time_departamentos and 
                                          (datetime.now() - last_load_time_departamentos > timedelta(minutes=CACHE_EXPIRATION_MINUTES))):
        print("Cargando datos de departamentos desde la base de datos...")
        engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/dwh_sociodemografico")
        df_cache_departamentos = pd.read_sql_query("SELECT * FROM censo_ipecd_departamentos", engine)
        last_load_time_departamentos = datetime.now()
    else:
        print("Usando datos desde caché...")
    return df_cache_departamentos

def read_data_censo_municipios():
    """Carga los datos de municipios desde la base de datos o desde caché."""
    global df_cache_municipios, last_load_time_municipios
    if df_cache_municipios is None or (last_load_time_municipios and 
                                       (datetime.now() - last_load_time_municipios > timedelta(minutes=CACHE_EXPIRATION_MINUTES))):
        print("Cargando datos de municipios desde la base de datos...")
        engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/dwh_sociodemografico")
        df_cache_municipios = pd.read_sql_query("SELECT * FROM censo_ipecd_municipios", engine)
        last_load_time_municipios = datetime.now()
    else:
        print("Usando datos desde caché...")
    return df_cache_municipios

# ------------------- Generar Teclado de Municipios -------------------
def generar_teclado_municipios(df):
    """Genera un teclado con los nombres de los municipios en orden alfabético, excluyendo valores inválidos."""
    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    # Extraer y ordenar los municipios alfabéticamente, ignorando "indeterminado"
    municipios = sorted([m for m in df['municipio'].unique() if m.lower() != "indeterminado"])

    # Agregar cada municipio como botón en el teclado
    for municipio in municipios:
        board.add(telebot.types.KeyboardButton(text=municipio))

    return board


# ------------------- Menú del Censo -------------------
def send_menu_censo(bot, message):
    """Muestra el menú principal del Censo."""
    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    board.add(
        telebot.types.KeyboardButton(text="Población Total en la Provincia"), 
        telebot.types.KeyboardButton(text="Población por municipio"),  
        telebot.types.KeyboardButton(text="Variación de la Población"),
        telebot.types.KeyboardButton(text="Peso de la Población"),
        telebot.types.KeyboardButton(text="Quiero saber de otro tema")
    )
    message_text = (
        "📊 *Información sobre los Departamentos y Municipios*\n"
        "Por favor selecciona la información que deseas conocer:\n\n"
        "👥 *1-Población Total en la Provincia*: Muestra la cantidad total de habitantes en Corrientes.\n"
        "🏘️ *2-Población por Municipio*: Muestra la población total de un municipio específico.\n"
        "📊 *3-Variación de la Población*: Comparación de población entre 2010 y 2022.\n"
        "⚖️ *4-Peso de la Población*: Muestra la proporción de la población en relación al total.\n"
        "\n🔙 *5-Quiero saber de otro tema*: Para regresar a la pantalla principal."
    )
    bot.send_message(message.chat.id, message_text, reply_markup=board, parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda m: resp_censo_departamento(m, bot))


# ------------------- Responder al Censo -------------------
def resp_censo_departamento(message, bot):
    """Gestiona las respuestas del usuario sobre el Censo."""
    opcion = message.text.lower().strip()
    df = read_data_censo_municipios()

    if opcion == "población total en la provincia":
        mostrar_total_poblacion(df, bot, message)  # Nuevo flujo más claro
    elif opcion == "población por municipio":
        mostrar_datos_todos_municipios(bot, message, df, "población")
    elif opcion == "variación de la población":
        mostrar_datos_todos_municipios(bot, message, df, "variación")
    elif opcion == "peso de la población":
        mostrar_datos_todos_municipios(bot, message, df, "peso")
    elif opcion == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre los datos del censo.")
        send_menu_principal(bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "⚠️ Opción no válida. Por favor, selecciona nuevamente.")
        send_menu_censo(bot, message)  # Volver al menú principal



# ------------------- RESPUESTAS DEL BOT -------------------
# ------------------- Mostrar Datos de Todos los Municipios -------------------
def mostrar_datos_todos_municipios(bot, message, df, tipo):
    """Muestra los datos de todos los municipios ordenados alfabéticamente."""
    municipios = df.sort_values('municipio')  # Ordenar alfabéticamente por municipio

    # Configurar locale para el formato de números español
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Linux/MacOS
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Spanish_Spain')  # Windows

    mensajes = []  # Lista para almacenar los mensajes generados

    # Recorrer cada fila del DataFrame para generar el mensaje correspondiente
    for _, row in municipios.iterrows():
        municipio = row['municipio']

        if tipo == "poblacion":
            poblacion = locale.format_string('%d', row['poblacion_viv_part_2022'], grouping=True)
            mensaje = f"🏘️ *{municipio}*: {poblacion} habitantes (2022).\n"
        elif tipo == "variacion":
            variacion = locale.format_string('%d', row['var_abs_poblacion_2010_vs_2022'], grouping=True)
            mensaje = f"📊 *{municipio}*: Variación de {variacion} habitantes entre 2010 y 2022.\n"
        elif tipo == "peso":
            peso_relativo = row['peso_relativo_2022']
            mensaje = f"⚖️ *{municipio}*: {peso_relativo:.2f}% del total de la población.\n"

        mensajes.append(mensaje)  # Agregar mensaje a la lista

    # Enviar los mensajes en bloques para evitar exceder el límite de 4096 caracteres
    mensaje_completo = "".join(mensajes)
    for i in range(0, len(mensaje_completo), 4096):  # Telegram permite máximo 4096 caracteres por mensaje
        bot.send_message(message.chat.id, mensaje_completo[i:i+4096], parse_mode="Markdown")

    # Volver al menú principal después de mostrar los datos
    send_menu_censo(bot, message)

# ------------------- Mostrar Población Total -------------------
def mostrar_total_poblacion(df, bot, message):
    """Muestra la población total en todos los municipios con formato adecuado."""
    # Configurar el locale para usar el formato español (con punto para miles)
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')  # Linux/MacOS
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'Spanish_Spain')  # Windows

    # Calcular la población total y formatear con puntos
    total_poblacion = df['poblacion_viv_part_2022'].sum()
    total_poblacion_modificada = locale.format_string('%d', total_poblacion, grouping=True)

    # Crear el mensaje con el valor formateado
    mensaje = (
        f"👥 *Población Total en la Provincia de Corrientes*:\n"
        f"{total_poblacion_modificada} habitantes."
    )

    # Enviar el mensaje al usuario
    bot.send_message(message.chat.id, mensaje, parse_mode="Markdown")

    # Volver al menú principal del censo
    send_menu_censo(bot, message)

"""
# ------------------- Opción: Ver Población por Municipio -------------------
def ver_poblacion_por_municipio(bot, message, df):
    Solicita al usuario seleccionar un municipio para ver su población.
    board = generar_teclado_municipios(df)
    bot.send_message(
        message.chat.id, 
        "🏘️ *Selecciona un municipio para ver su población total*:", 
        reply_markup=board, 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, lambda m: mostrar_datos_municipio(m, bot, df, "poblacion"))

# ------------------- Ver Variación de Población -------------------
def ver_variacion_por_municipio(bot, message, df):
    Solicita un municipio para mostrar la variación de la población.
    board = generar_teclado_municipios(df)
    bot.send_message(
        message.chat.id, 
        "📊 *Selecciona un municipio para ver la variación poblacional*:", 
        reply_markup=board, 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, lambda m: mostrar_datos_municipio(m, bot, df, "variacion"))


# ------------------- Ver Peso Relativo de Población -------------------
def ver_peso_por_municipio(bot, message, df):
    Solicita un municipio para mostrar el peso relativo de la población.
    board = generar_teclado_municipios(df)
    bot.send_message(
        message.chat.id, 
        "Selecciona un municipio para ver su peso relativo:", 
        reply_markup=board
    )
    bot.register_next_step_handler(message, lambda m: mostrar_datos_municipio(m, bot, df, "peso"))"""