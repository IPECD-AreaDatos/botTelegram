import sqlalchemy
import locale
import pandas as pd
import pymysql
import telebot
from src.helpers.bot_helpers import send_menu_principal
from datetime import datetime, timedelta

engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/datalake_economico")
df_cache = pd.read_sql_query("SELECT * FROM ipicorr", engine)
columns_to_multiply = [
    'Var_Interanual_IPICORR', 
    'Var_Interanual_Alimentos', 
    'Var_Interanual_Textil', 
    'Var_Interanual_Maderas', 
    'Var_Interanual_MinNoMetalicos', 
    'Var_Interanual_Metales'
]
df_cache[columns_to_multiply] = df_cache[columns_to_multiply] * 100


promedio = (df_cache['Var_Interanual_IPICORR'].iloc[-3] + df_cache['Var_Interanual_IPICORR'].iloc[-2] + df_cache['Var_Interanual_IPICORR'].iloc[-1]) / 3
print(f"Promedio: {promedio:.2f}%")