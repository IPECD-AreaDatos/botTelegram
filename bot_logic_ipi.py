import sqlalchemy
import pandas as pd
import telebot
from bot_helpers import send_menu_principal

def read_data_ipi():
    engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/datalake_economico")
    df = pd.read_sql_query("SELECT * FROM ipi_valores", engine)
    return df

def resp_ipi(message, bot):
    #df = read_data_ipi()
    user_input = message.text.lower()

    if user_input == "¿que es?":
        bot.send_message(message.chat.id, "El índice de producción industrial manufacturero (IPI manufacturero) incluye un exhaustivo relevamiento de todas las actividades económicas que conforman el sector de la industria manufacturera.")
        bot.register_next_step_handler(message, lambda m: resp_ipi(m, bot))

    elif user_input == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre IPI. ¿En qué más puedo ayudarte?")
        send_menu_principal(bot, message.chat.id)  # Usar la función para enviar el menú principal
        
    else:
        bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
        bot.register_next_step_handler(message, lambda m: resp_ipi(m, bot))
