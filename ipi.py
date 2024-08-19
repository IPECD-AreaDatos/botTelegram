import sqlalchemy
import pandas as pd
import pymysql
import telebot

from handlers import setup_handlers

def read_data():
    engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/datalake_economico")
    df = pd.read_sql_query("SELECT * FROM ipi_valores", engine)
    print(df)
    return df

def resp_ipi(message, bot):
    df = read_data()
    user_input = message.text.lower()

    if user_input == "que es?":
        bot.send_message(message.chat.id, "El índice de producción industrial manufacturero (IPI manufacturero) incluye un exhaustivo relevamiento de todas las actividades económicas que conforman el sector de la industria manufacturera, con cobertura para el total del país.Este indicador mide la evolución del sector con periodicidad mensual y se calcula a partir de las variables de producción en unidades físicas, ventas en unidades físicas, utilización de insumos en unidades físicas, consumo aparente en unidades físicas, cantidad de horas trabajadas del personal afectado al proceso productivo y ventas a precios corrientes deflactadas.")
        bot.register_next_step_handler(message, lambda m: resp_ipi(m, bot))  # Mantiene al usuario en la misma función

    elif user_input == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre IPI. ¿En qué más puedo ayudarte?")
        setup_handlers(bot)
        
    else:
        bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
        bot.register_next_step_handler(message, lambda m: resp_ipi(m, bot)) 
