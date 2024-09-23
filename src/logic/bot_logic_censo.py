import sqlalchemy
import locale
import pandas as pd
import pymysql
import telebot
from helpers.bot_helpers import send_menu_principal
from datetime import datetime, timedelta
import unicodedata

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
    if message.text.lower() == "departamentos":
        df = read_data_censo_departamentos()
        board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="Cantidad de Población"),
            telebot.types.KeyboardButton(text="Variacios Relativa"),
            telebot.types.KeyboardButton(text="Densidad de habitantes por km²")
        )
        bot.send_message(message.chat.id, "¿En qué quieres obtener información?", reply_markup=board)
        bot.register_next_step_handler(message, lambda m: resp_censo_departamento(m, bot, df))
    elif message.text.lower() == "municipios":
        df = read_data_censo_municipios

def resp_censo_departamento(message, bot, df):
    if message.text.lower() == "Cantidad de Población":
        board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        board.add(
            telebot.types.KeyboardButton(text="Total"),
            telebot.types.KeyboardButton(text="Bella Vista"),
            telebot.types.KeyboardButton(text="Berón de Astrada"),
            telebot.types.KeyboardButton(text="Capital"),
            telebot.types.KeyboardButton(text="Concepción"),
            telebot.types.KeyboardButton(text="Curuzú Cuatiá"),
            telebot.types.KeyboardButton(text="Empedrado"),
            telebot.types.KeyboardButton(text="Esquina"),
            telebot.types.KeyboardButton(text="General Alvear"),
            telebot.types.KeyboardButton(text="General Paz"),
            telebot.types.KeyboardButton(text="Goya"),
            telebot.types.KeyboardButton(text="Itatí"),
            telebot.types.KeyboardButton(text="Ituzaingó"),
            telebot.types.KeyboardButton(text="Lavalle"),
            telebot.types.KeyboardButton(text="Mburucuyá"),
            telebot.types.KeyboardButton(text="Mercedes"),
            telebot.types.KeyboardButton(text="Monte Caseros"),
            telebot.types.KeyboardButton(text="Paso de los Libres"),
            telebot.types.KeyboardButton(text="Saladas"),
            telebot.types.KeyboardButton(text="San Cosme"),
            telebot.types.KeyboardButton(text="San Luis del Palmar"),
            telebot.types.KeyboardButton(text="San Martín"),
            telebot.types.KeyboardButton(text="San Miguel"),
            telebot.types.KeyboardButton(text="San Roque"),
            telebot.types.KeyboardButton(text="Santo Tome"),
            telebot.types.KeyboardButton(text="Sauce")
        )
