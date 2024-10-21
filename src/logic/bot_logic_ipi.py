import sqlalchemy
import pandas as pd
from helpers.bot_helpers import send_menu_principal
import locale
import telebot
import matplotlib.pyplot as plt

# ------------------ Carga de Datos y Configuración ------------------
def read_data_ipi():
    """Carga los datos de IPI Nación desde la base de datos y prepara el DataFrame."""
    engine = sqlalchemy.create_engine(
        "mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/datalake_economico"
    )
    df = pd.read_sql_query("SELECT * FROM ipi_valores", engine)

    # Eliminar filas completamente vacías
    df = df.dropna(how='all')

    # Convertir la columna 'fecha' a tipo datetime
    df['fecha'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y')

    # Multiplicar las columnas de variación por 100 para convertirlas en porcentajes
    cols_to_multiply = [
        'var_mensual_ipi_manufacturero', 'var_mensual_alimentos',
        'var_mensual_textil', 'var_mensual_maderas', 'var_mensual_sustancias',
        'var_mensual_min_no_metalicos', 'var_mensual_min_metales'
    ]
    df[cols_to_multiply] = df[cols_to_multiply] * 100

    return df

# ----------------- Gestión de Fechas en Español -----------------
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

# ------------------- Menú Principal de IPI Nación -------------------
def send_menu_ipi_nacion(bot, message):
    """Envía el menú de IPI Nación al usuario."""
    hide_board = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Cargando menú de IPI Nación...", reply_markup=hide_board)

    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    opciones = [
        "¿Que es IPI Nacion?", "Ultimo valor", "Ver grafico", 
        "Consulta personalizada", "Volver al menú principal"
    ]
    for opcion in opciones:
        board.add(telebot.types.KeyboardButton(text=opcion))

    bot.send_message(message.chat.id, "¿Qué tema quieres saber sobre IPI Nación?", reply_markup=board)
    bot.register_next_step_handler(message, lambda m: resp_ipi_nacion(m, bot))

# ------------------- Respuestas del Bot -------------------
def resp_ipi_nacion(message, bot):
    """Maneja las respuestas del usuario sobre IPI Nación."""
    df = read_data_ipi()
    user_input = message.text.lower().strip()

    if user_input == "¿que es ipi nacion?":
        bot.send_message(message.chat.id, (
            "El índice de producción industrial manufacturero (IPI) mide el desempeño "
            "de distintas actividades industriales en el país."
        ))
        bot.register_next_step_handler(message, lambda m: resp_ipi_nacion(m, bot))
    elif user_input == "ultimo valor":
        ultimo_valor_ipi(df, bot, message)
    elif user_input == "ver grafico":
        pedir_sector_ipi(bot, message)
    elif user_input == "consulta personalizada":
        bot.send_message(message.chat.id, "Consulta personalizada no disponible aún.")
        send_menu_ipi_nacion(bot, message)
    elif user_input == "volver al menú principal":
        send_menu_principal(bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Opción no válida. Elige nuevamente.")
        bot.register_next_step_handler(message, lambda m: resp_ipi_nacion(m, bot))

def ultimo_valor_ipi(df, bot, message):
    """Muestra el último valor de las variaciones mensuales del IPI Nacional y sus sectores."""
    ultimo_registro = df.iloc[-1]
    fecha = ultimo_registro['fecha']
    mensaje = (
        f"Variaciones mensuales del IPI Nacional - {get_fecha_en_espanol(fecha)}:\n"
        f"- IPI Manufacturero: {ultimo_registro['var_mensual_ipi_manufacturero']:.1f}%\n"
        f"- Alimentos: {ultimo_registro['var_mensual_alimentos']:.1f}%\n"
        f"- Textil: {ultimo_registro['var_mensual_textil']:.1f}%\n"
        f"- Maderas: {ultimo_registro['var_mensual_maderas']:.1f}%\n"
        f"- Sustancias: {ultimo_registro['var_mensual_sustancias']:.1f}%\n"
        f"- Minerales no metálicos: {ultimo_registro['var_mensual_min_no_metalicos']:.1f}%\n"
        f"- Metales: {ultimo_registro['var_mensual_min_metales']:.1f}%"
    )
    bot.send_message(message.chat.id, mensaje)
    send_menu_ipi_nacion(bot, message)
# ------------------- Generación de Gráficos -------------------
def pedir_sector_ipi(bot, message):
    """Solicita al usuario que seleccione el sector del IPI para graficar."""
    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    sectores = [
        "IPI Manufacturero", "Alimentos", "Textil", "Maderas", 
        "Sustancias", "Minerales no metálicos", "Metales", "Volver"
    ]
    for sector in sectores:
        board.add(telebot.types.KeyboardButton(text=sector))

    bot.send_message(message.chat.id, "¿Qué sector del IPI Nación quieres graficar?", reply_markup=board)
    bot.register_next_step_handler(message, lambda m: pedir_meses_ipi(m, bot, m.text))

def pedir_meses_ipi(message, bot, sector):
    """Solicita el número de meses para graficar el sector seleccionado."""
    valid_sectors = {
        "ipi manufacturero": "var_mensual_ipi_manufacturero",
        "alimentos": "var_mensual_alimentos",
        "textil": "var_mensual_textil",
        "maderas": "var_mensual_maderas",
        "sustancias": "var_mensual_sustancias",
        "minerales no metálicos": "var_mensual_min_no_metalicos",
        "metales": "var_mensual_min_metales"
    }

    sector_key = sector.lower().strip()

    if sector_key not in valid_sectors:
        bot.send_message(message.chat.id, "Sector no válido. Por favor selecciona uno de la lista.")
        pedir_sector_ipi(bot, message)
        return

    bot.send_message(message.chat.id, f"¿Cuántos meses quieres mostrar para {sector}?")
    bot.register_next_step_handler(message, lambda m: generar_y_enviar_grafico_ipi(m, bot, valid_sectors[sector_key]))

def generar_y_enviar_grafico_ipi(message, bot, sector):
    """Genera y envía el gráfico del sector seleccionado."""
    try:
        meses = int(message.text.strip())
        if meses <= 0:
            raise ValueError("El número de meses debe ser mayor que 0.")

        df = read_data_ipi()
        generar_grafico_ipi(df, sector, meses)

        with open('grafico_ipi.png', 'rb') as foto:
            bot.send_photo(message.chat.id, foto, caption=f"Evolución de {sector} - Últimos {meses} meses")
        send_menu_ipi_nacion(bot, message)

    except ValueError:
        bot.send_message(message.chat.id, "Por favor, ingresa un número válido.")
        pedir_meses_ipi(bot, message, sector)

def generar_grafico_ipi(df, sector, meses):
    """Genera el gráfico del sector seleccionado con las variaciones mensuales."""
    df = df.sort_values('fecha').tail(meses)
    plt.figure(figsize=(10, 6))
    plt.plot(df['fecha'], df[sector], marker='o', linestyle='-', label=sector)
    for i, row in df.iterrows():
        plt.annotate(f"{row[sector]:.1f}%", (row['fecha'], row[sector]), textcoords="offset points", xytext=(0, 10), ha='center')
    plt.title(f'Evolución de {sector} (variación mensual)', fontsize=16)
    plt.xlabel('Fecha')
    plt.ylabel('Variación (%)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('grafico_ipi.png')
    plt.close()
