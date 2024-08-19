import sqlalchemy
import pandas as pd
import pymysql
import telebot

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

    if user_input == "que es?":
        bot.send_message(message.chat.id, "La Dirección de Estadística y Censos en conjunto con el Ministerio de Industria, trabaja en el Índice de Producción Industrial manufacturero de la provincia de Corrientes (IPICorr). El mismo reúne información de las principales empresas industriales que producen y comercializan productos. Su objetivo es medir la evolución mensual de la actividad económica de la industria en la provincia.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))  # Mantiene al usuario en la misma función
        
    elif user_input == "ultimo valor":
        last_value = df['Var_Interanual_IPICORR'].iloc[-1]
        bot.send_message(message.chat.id, f"El valor actual del IPICORR es: %{last_value :.2f}")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))  # Mantiene al usuario en la misma función
        
    elif user_input == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre IPICORR. ¿En qué más puedo ayudarte?")
        # Aquí puedes cambiar a otro handler o simplemente permitir que el usuario elija otro tema.
        
    else:
        bot.send_message(message.chat.id, "Opción no válida, por favor elige de nuevo.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))  # Mantiene al usuario en la misma función