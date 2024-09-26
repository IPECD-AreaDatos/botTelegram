import sqlalchemy
import locale
import pandas as pd
import pymysql
import telebot
from helpers.bot_helpers import send_menu_principal
from datetime import datetime, timedelta
import unicodedata
from functools import partial

df_cache = None
last_load_time = None
CACHE_EXPIRATION_MINUTES = 30

def read_data_censo_departamentos():
    global df_cache, last_load_time

    if df_cache is None or (last_load_time and (datetime.now() - last_load_time > timedelta(minutes=CACHE_EXPIRATION_MINUTES))):
        print("Cargando datos desde la base de datos...")
        engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/dwh_sociodemografico")
        df_cache = pd.read_sql_query("SELECT * FROM censo_ipecd_departamentos", engine)
    else:
        print ("Usando datos desde caché...")
    return df_cache

def read_data_censo_municipios():
    global df_cache, last_load_time

    if df_cache is None or (last_load_time and (datetime.now() - last_load_time > timedelta(minutes=CACHE_EXPIRATION_MINUTES))):
        print("Cargando datos desde la base de datos...")
        engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/dwh_sociodemografico")
        df_cache = pd.read_sql_query("SELECT * FROM censo_ipecd_municipios", engine)
    else:
        print ("Usando datos desde caché...")
    return df_cache

def resp_censo(message, bot):
    if message.text.lower() == "quiero saber mas":
        df = read_data_censo_municipios()  # Aquí lees los datos de departamentos (ajuste correcto)
        board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="Cantidad de Población"),
            telebot.types.KeyboardButton(text="Variación de la Población"),
            telebot.types.KeyboardButton(text="Peso de la Población"),
            telebot.types.KeyboardButton(text="Volver al menu principal")
        )
        message_text = (
            "📊 *Información sobre los Departamentos*\n"
            "Por favor selecciona la información que deseas conocer:\n\n"
            "🏘️ *Cantidad de Población*: Muestra el número total de habitantes.\n"
            "📊 *Variación de la Población*: Comparación de población entre 2010 y 2022.\n"
            "⚖️ *Peso de la Población*: Muestra la proporción de la población en relación al total.\n"
            "\n🔙 *Volver al menú principal*: Para regresar a la pantalla principal."
        )
        bot.send_message(message.chat.id, message_text, reply_markup=board, parse_mode="Markdown")
        bot.register_next_step_handler(message, lambda m: resp_censo_departamento(m, bot, df))  # Mantener bot y df
    
    elif message.text.lower() == "municipios":
        df = read_data_censo_municipios()  # Aquí lees los datos de municipios
        # Lógica para manejar municipios si es necesario
    elif message.text.lower() == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre Censo. ¿En qué más puedo ayudarte?")
        send_menu_principal(bot, message.chat.id)  # Envía el menú principal

def resp_censo_departamento(message, bot, df):
    # Aquí gestionamos si el usuario selecciona "Cantidad de Población", "Variación de la Población" o "Peso"
    opcion = ""
    if message.text.lower() == "cantidad de población":
        opcion = "cantidad poblacion"
    elif message.text.lower() == "variación de la población":
        opcion = "variacion poblacion"
    elif message.text.lower() == "peso de la población":
        opcion = "peso relativo"
    elif message.text.lower() == "volver al menu principal":
        send_menu_principal(bot, message.chat.id)
        return
    # Mostramos la lista de municipios
    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    municipios = [
        "Pago de los Deseos (2012)", "San Isidro (2013)", "Palmar Grande", "Colonia Carlos Pellegrini", "Tapebicuá",
        "Cazadores Correntinos (2018)", "Garruchos", "Bonpland", "San Antonio Isla Apipé Grande", "Pueblo Libertador",
        "San Carlos", "Parada Pucheta", "Caá Catí", "Lomas de Vallejos", "Guaviraví", "Colonia Libertad", 
        "Gobernador Virasoro", "San Roque", "Villa Olivari", "Colonia Liebig", "Tres de Abril (2011)", "Alvear",
        "Yapeyú", "San Antonio de Itatí", "Sauce", "El Sombrero (2014)", "Loreto", "Pedro R. Fernández", 
        "Paso de los Libres", "Concepción del Yaguareté Corá", "La Cruz", "Perugorría", "Manuel Derqui (2021)", 
        "Cruz de los Milagros", "San Luis del Palmar", "Ramada Paso", "Curuzú Cuatiá", "Colonia Pando", "Tatacuá",
        "San Miguel", "Corrientes", "Mercedes", "9 de julio", "Garaví", "Monte Caseros", "Tabay", "Santo Tomé",
        "Cecilio Echavarría (2018)", "Mburucuyá", "Gobernador Martínez", "Itá Ibaté", "Chavarría", "Estación Torrent",
        "Goya", "Santa Rosa", "Esquina", "Mocoretá", "San Cosme", "Mariano I. Loza", "Bella Vista", "Ituzaingó", 
        "Itatí", "Felipe Yofré", "Paso de la Patria", "San Lorenzo", "Yatay Ti Calle", "Santa Ana de los Guácaras", 
        "Santa Lucía", "Carolina", "Empedrado", "Saladas", "Juan Pujol", "Lavalle", "Riachuelo", "Herlitzka"
    ]

    for municipio in municipios:
        board.add(telebot.types.KeyboardButton(text=municipio))

    bot.send_message(message.chat.id, "Selecciona un municipio para obtener información:", reply_markup=board)
    bot.register_next_step_handler(message, lambda m: mostrar_datos_departamento(m, bot, df, opcion, "departamentos"))

def mostrar_datos_departamento(message, bot, df, opcion, contexto):
    # Mostramos los datos según la opción seleccionada
    departamento = message.text  # Nombre del departamento/municipio seleccionado
    datos_departamento = df[df['municipio'] == departamento]  # Filtra el DataFrame por el departamento seleccionado
    
    if not datos_departamento.empty:
        nombre_municipio = f"📍 *Datos del municipio {departamento}*:\n"
        
        if opcion == "cantidad poblacion":
            poblacion = datos_departamento['poblacion_viv_part_2022'].values[0]
            mensaje = (
                f"{nombre_municipio}"
                f"👥 *Población Total*: {poblacion:,} habitantes\n"
            )
        elif opcion == "variacion poblacion":
            variacion = datos_departamento['var_abs_poblacion_2010_vs_2022'].values[0]
            mensaje = (
                f"{nombre_municipio}"
                f"📊 *Variación Poblacional*: {variacion:,} habitantes entre 2010 y 2022\n"
            )
        elif opcion == "peso relativo":
            peso = datos_departamento['peso_relativo_2022'].values[0]
            mensaje = (
                f"{nombre_municipio}"
                f"⚖️ *Peso Relativo*: {peso}% de la población total\n"
            )
        # Enviar el mensaje con los datos
        bot.send_message(message.chat.id, mensaje)

        # Volver al menú principal después de mostrar la información
        send_menu_censo(bot, message)
    else:
        bot.send_message(message.chat.id, "No se encontraron datos para el municipio seleccionado.")
        send_menu_censo(bot, message)

def send_menu_censo(bot, message):
    # Volver al menú inicial del Censo
    df = read_data_censo_municipios()  # Aquí lees los datos de departamentos (ajuste correcto)
    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    board.add(
        telebot.types.KeyboardButton(text="Cantidad de Población"),
        telebot.types.KeyboardButton(text="Variación de la Población"),
        telebot.types.KeyboardButton(text="Peso de la Población"),
        telebot.types.KeyboardButton(text="Volver al menu principal")
    )
    message_text = (
        "📊 *Información sobre los Departamentos*\n"
        "Por favor selecciona la información que deseas conocer:\n\n"
        "🏘️ *Cantidad de Población*: Muestra el número total de habitantes.\n"
        "📊 *Variación de la Población*: Comparación de población entre 2010 y 2022.\n"
        "⚖️ *Peso de la Población*: Muestra la proporción de la población en relación al total.\n"
        "\n🔙 *Volver al menú principal*: Para regresar a la pantalla principal."
    )
    bot.send_message(message.chat.id, message_text, reply_markup=board, parse_mode="Markdown")
    bot.register_next_step_handler(message, lambda m: resp_censo_departamento(m, bot, df))  # Mantener bot y df

