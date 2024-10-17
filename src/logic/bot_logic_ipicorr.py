import sqlalchemy
import locale
import pandas as pd
import matplotlib.pyplot as plt
import telebot
from helpers.bot_helpers import send_menu_principal
from datetime import datetime, timedelta
import locale

#----------------------Variables globales para almacenar el dataframe y la fecha de carga----------------------
df_cache = None
last_load_time = None
CACHE_EXPIRATION_MINUTES = 30  # Duración del cache

def load_data():
    """Carga los datos si no están en caché o si el caché ha expirado."""
    global df_cache, last_load_time

    try:
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
            last_load_time = datetime.now()
        else:
            print("Usando datos desde caché...")
    except Exception as e:
        print(f"Error al cargar los datos: {str(e)}")
        df_cache = None  # Restablecemos el caché para intentar cargarlo más adelante

    return df_cache

#----------------------Gestion de fechas en español----------------------
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Linux/MacOS
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Spanish_Spain')  # Windows

def get_fecha_en_espanol(fecha):
    """Devuelve la fecha formateada en español."""
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'es_ES')

    fecha_en_espanol = fecha.strftime('%B %Y').capitalize()
    return fecha_en_espanol

#----------------------Menus y navegacion del IPICORR----------------------
def send_menu_ipicorr(bot, message):
    """Envía el menú de IPICORR al usuario."""
    hide_board = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Cargando menú de IPICORR...", reply_markup=hide_board)

    # Crear el nuevo menú
    board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    opciones = [
        "¿Que es IPICORR?", "Ultimo valor", "Ver variaciones(categorias)",
        "¿Cual es la tendencia en los ultimos años?", "Ver grafico",
        "Consulta personalizada", "Quiero saber de otro tema"
    ]
    for opcion in opciones:
        board.add(telebot.types.KeyboardButton(text=opcion))

    bot.send_message(message.chat.id, "¿Qué tema quieres saber sobre IPICORR?", reply_markup=board)
    bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))

def volver_al_menu(bot, message, menu_func):
    """Redirige al submenú o menú principal según la opción seleccionada."""
    user_input = message.text.strip().lower()

    # Remover el teclado anterior antes de cambiar al nuevo menú
    hide_board = telebot.types.ReplyKeyboardRemove()

    if user_input == "volver":
        bot.send_message(message.chat.id, "Volviendo...", reply_markup=hide_board)
        menu_func(bot, message)  # Redirige al submenú correspondiente
    elif user_input == "volver al menú principal":
        bot.send_message(message.chat.id, "Volviendo al menú principal...", reply_markup=hide_board)
        send_menu_principal(bot, message.chat.id)  # Va al menú principal
    else:
        bot.send_message(message.chat.id, "Opción no válida. Elige nuevamente.", reply_markup=hide_board)
        menu_func(bot, message)  # Vuelve al submenú para elegir otra opción

#----------------------Respuestas del Bot y Flujos de Trabajo----------------------
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
        fecha_texto = get_fecha_en_espanol(fecha)

        bot.send_message(
            message.chat.id, 
            f"El último valor de IPICORR es: {last_value:.1f}% correspondiente a {fecha_texto}"
        )
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))

    elif user_input == "variaciones(categorias)":
        mostrar_menu_variaciones(bot, message)

    elif user_input == "¿cual es la tendencia en los ultimos años?":
        mostrar_menu_tendencias(bot, message)

    elif user_input == "ver grafico":
        pedir_meses_grafico(bot, message)

    elif user_input == "consulta personalizada":
        pedir_fecha_personalizada(bot, message)

    elif user_input == "quiero saber de otro tema":
        bot.send_message(message.chat.id, "Gracias por consultar sobre IPICORR.")
        send_menu_principal(bot, message.chat.id)
    
    else:
        bot.send_message(message.chat.id, "Opción no válida. Elige nuevamente.")
        bot.register_next_step_handler(message, lambda m: resp_ipicorr(m, bot))

#----------------------Variaciones----------------------
def mostrar_menu_variaciones(bot, message):
    """Muestra el menú de variaciones interanuales."""
    # Remover cualquier teclado anterior
    hide_board = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Cargando variaciones...", reply_markup=hide_board)

    # Crear el nuevo teclado para las variaciones
    board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    opciones = [
        "Interanual IPICORR", "Interanual Alimentos", "Interanual Textil",
        "Interanual Maderas", "Interanual Minerales No Metalicos", 
        "Interanual Metales", "Volver", "Volver al menú principal"
    ]
    for opcion in opciones:
        board.add(telebot.types.KeyboardButton(text=opcion))

    bot.send_message(message.chat.id, "¿Qué variación deseas consultar?", reply_markup=board)
    bot.register_next_step_handler(message, lambda m: resp_ipicorr_variaciones(m, bot, df_cache))

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
        bot.send_message(
            message.chat.id, 
            f"El último valor de {user_input} es: {last_value:.1f}% correspondiente a {fecha_texto}"
        )
        # Volvemos a mostrar el menú de variaciones
        mostrar_menu_variaciones(bot, message)

    elif user_input == "volver":
        # Remover teclado y enviar el menú principal de IPICORR
        hide_board = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Volviendo al menú de IPICORR...", reply_markup=hide_board)
        send_menu_ipicorr(bot, message)  # Volvemos al menú principal de IPICORR

    elif user_input == "volver al menú principal":
        hide_board = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Volviendo al menú principal...", reply_markup=hide_board)
        send_menu_principal(bot, message.chat.id)  # Volvemos al menú principal

    else:
        bot.send_message(message.chat.id, "Opción no válida. Elige nuevamente.")
        mostrar_menu_variaciones(bot, message)  # Volvemos a mostrar el menú de variaciones

#----------------------Tendencias----------------------
def mostrar_menu_tendencias(bot, message):
    """Muestra el menú para consultar tendencias por año."""
    # Remover cualquier teclado anterior
    hide_board = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Cargando menú de tendencias...", reply_markup=hide_board)

    # Crear el nuevo teclado de tendencias
    board = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    board.add(
        telebot.types.KeyboardButton(text="2022"),
        telebot.types.KeyboardButton(text="2023"),
        telebot.types.KeyboardButton(text="2024"),
        telebot.types.KeyboardButton(text="Volver"),
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

        # Volvemos al menú de tendencias para seguir consultando
        mostrar_menu_tendencias(bot, message)

    elif user_input.lower() == "volver":
        # Remover el teclado y regresar al menú IPICORR
        hide_board = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Volviendo al menú de IPICORR...", reply_markup=hide_board)
        send_menu_ipicorr(bot, message)

    elif user_input.lower() == "volver al menú principal":
        # Remover el teclado y regresar al menú principal
        hide_board = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Volviendo al menú principal...", reply_markup=hide_board)
        send_menu_principal(bot, message.chat.id)

    else:
        bot.send_message(message.chat.id, "Por favor selecciona un año válido.")
        mostrar_menu_tendencias(bot, message)  # Mostrar el menú de nuevo

def calcular_promedio_anual(df, año):
    """Calcula el promedio de variaciones para un año completo."""
    datos_anuales = df[df['Fecha'].dt.year == año]

    if datos_anuales.empty:
        return f"No hay datos disponibles para el año {año}."

    promedio = datos_anuales['Var_Interanual_IPICORR'].mean()
    return f"El promedio de variación interanual en {año} fue de {promedio:.1f}%."

#----------------------Generacion de Graficos----------------------
def pedir_meses_grafico(bot, message):
    """Solicita al usuario el número de meses para el gráfico."""
    bot.send_message(message.chat.id, "¿Cuántos meses quieres mostrar en el gráfico?Responda con un número mayor que 0")
    bot.register_next_step_handler(message, lambda m: generar_y_enviar_grafico(m, bot))

def generar_y_enviar_grafico(message, bot):
    """Genera y envía el gráfico según el número de meses indicado por el usuario."""
    try:
        # Validar que el usuario ingresó un número
        meses = int(message.text.strip())
        if meses <= 0:
            raise ValueError("El número de meses debe ser mayor que 0.")

        df = load_data()
        if df is None:
            bot.send_message(message.chat.id, "No se pudieron cargar los datos. Inténtalo más tarde.")
            return

        generar_grafico_ipicorr(df, meses)  # Generar el gráfico

        # Enviar el gráfico al usuario
        with open('grafico_ipicorr.png', 'rb') as foto:
            bot.send_photo(message.chat.id, foto, caption=f"Evolución del IPICORR - Últimos {meses} meses")
        # Redirigir al usuario al menú principal de IPICORR después de mostrar el gráfico
        bot.send_message(message.chat.id, "¿Hay algo más con lo que pueda ayudarte?")
        send_menu_ipicorr(bot, message)

    except ValueError:
        bot.send_message(message.chat.id, "Por favor ingresa un número válido de meses.")
        pedir_meses_grafico(bot, message)  # Volver a pedir el número de meses
    except Exception as e:
        bot.send_message(message.chat.id, f"Ocurrió un error inesperado: {str(e)}")


def generar_grafico_ipicorr(df, meses):
    """Genera un gráfico con la evolución del IPICORR para los últimos N meses y muestra los valores en los puntos."""
    # Ordenar los datos por fecha y seleccionar los últimos 'meses' datos
    df = df.sort_values('Fecha').tail(meses)

    # Crear la figura y el gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(df['Fecha'], df['Var_Interanual_IPICORR'], marker='o', linestyle='-', color='b', label='IPICORR')

    # Añadir valores en cada punto
    for i, row in df.iterrows():
        plt.annotate(f"{row['Var_Interanual_IPICORR']:.1f}%", 
                     (row['Fecha'], row['Var_Interanual_IPICORR']), 
                     textcoords="offset points", 
                     xytext=(0, 10),  # Desplazamiento del texto
                     ha='center')

    # Configurar el título y las etiquetas
    plt.title(f'Evolución del IPICORR - Últimos {meses} meses', fontsize=16)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Variación Interanual (%)', fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)  # Rotar las etiquetas del eje X
    plt.tight_layout()  # Ajustar el gráfico para evitar superposición

    # Guardar la imagen
    plt.savefig('grafico_ipicorr.png')
    plt.close()  # Cerrar la figura para liberar memoria

#----------------------Consulta personalizada----------------------
def pedir_fecha_personalizada(bot, message):
    """Solicita al usuario una fecha para la consulta personalizada."""
    df = load_data()
    bot.send_message(message.chat.id, "¿Qué fecha deseas consultar? (ejemplo: marzo 2024)")
    bot.register_next_step_handler(message, lambda m: consultar_fecha_personalizada(m, bot))

def consultar_fecha_personalizada(message, bot):
    """Consulta el valor de IPICORR para la fecha proporcionada por el usuario."""
    fecha_texto = message.text.strip()
    df = load_data()

    if df is None:
        bot.send_message(message.chat.id, "No se pudieron cargar los datos. Inténtalo más tarde.")
        return

    respuesta = buscar_valor_por_fecha(df, fecha_texto)
    bot.send_message(message.chat.id, respuesta)

    # Si la fecha no es válida, volvemos a preguntar
    if "no tiene un formato válido" in respuesta or "No se encontraron datos" in respuesta:
        bot.send_message(message.chat.id, "Intenta con otra fecha. Ejemplo: marzo 2024")
        bot.register_next_step_handler(message, lambda m: consultar_fecha_personalizada(m, bot))
    else:
        # Confirmación opcional si la consulta fue exitosa
        send_menu_ipicorr(bot, message)

def buscar_valor_por_fecha(df, fecha_texto):
    """Busca el valor de IPICORR para una fecha específica proporcionada por el usuario."""
    try:
        # Normalizar la entrada del usuario
        fecha_texto = fecha_texto.strip().lower()
        fecha_texto = fecha_texto.capitalize()  # Asegurar que el mes esté capitalizado

        # Convertir la fecha ingresada a datetime
        fecha = pd.to_datetime(fecha_texto, format='%B %Y', errors='coerce')

        # Verificar si la conversión falló
        if pd.isna(fecha):
            return f"La fecha {fecha_texto} no tiene un formato válido. Inténtalo de nuevo."

        # Verificar si la fecha está en el DataFrame
        if fecha not in df['Fecha'].values:
            return f"No se encontraron datos para la fecha {fecha_texto}."

        # Obtener el valor correspondiente
        valor = df.loc[df['Fecha'] == fecha, 'Var_Interanual_IPICORR'].values[0]
        return f"El valor de IPICORR en {fecha_texto} fue de {valor:.1f}%."
    except Exception as e:
        return f"Ocurrió un error: {str(e)}"



