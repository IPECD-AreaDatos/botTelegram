import sqlalchemy
import pandas as pd
from helpers.bot_helpers import send_menu_principal
import locale
import telebot
import matplotlib.pyplot as plt
import calendar
import unidecode

# ------------------ Carga de Datos y Configuración ------------------
def read_data_ipi():
    """Carga los datos de IPI Nación desde la base de datos y prepara el DataFrame."""
    engine = sqlalchemy.create_engine("mysql+pymysql://estadistica:Estadistica2024!!@54.94.131.196:3306/datalake_economico")
    df = pd.read_sql_query("SELECT * FROM ipi_valores", engine)

    # Eliminar filas vacías
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

    # Calcular las variaciones anuales comparando con el mismo mes del año anterior
    for col in cols_to_multiply:
        df[f'anual_{col}'] = df[col].pct_change(periods=12) * 100

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

def convertir_a_fecha(texto):
    """Convierte una entrada 'mes año' a un objeto datetime."""
    try:
        # Normalizamos el texto: quitamos tildes y espacios en blanco
        texto = unidecode.unidecode(texto.strip().lower())
        mes, año = texto.split()

        # Intentamos obtener el número del mes
        mes_numero = next(
            (i for i, m in enumerate(calendar.month_name) if m.lower() == mes), 
            None
        )

        if mes_numero is None:  # Si no se encuentra el mes, devolvemos None
            return None

        # Construimos la fecha en formato datetime
        return pd.to_datetime(f"01/{mes_numero}/{año}", format='%d/%m/%Y')

    except (ValueError, IndexError):
        return None  # Si hay error en la conversión, devolvemos None

# ------------------- Menú Principal de IPI Nación -------------------
def send_menu_ipi_nacion(bot, message):
    """Envía el menú de IPI Nación al usuario."""
    hide_board = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Cargando menú de IPI Nación...", reply_markup=hide_board)

    board = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    opciones = [
        "¿Que es IPI Nacion?", "Ultimo valor", "Ver grafico", 
        "Consulta personalizada", "Comparar por fechas", "Volver al menu principal"
    ]
    for opcion in opciones:
        board.add(telebot.types.KeyboardButton(text=opcion))

    bot.send_message(message.chat.id, "¿Qué tema quieres saber sobre IPI Nación?(Escribe Volver al menu principal para salir)", reply_markup=board)
    bot.register_next_step_handler(message, lambda m: resp_ipi_nacion(m, bot))

# ------------------- Respuestas del Bot -------------------
def resp_ipi_nacion(message, bot):
    """Maneja las respuestas del usuario sobre IPI Nación."""
    df = read_data_ipi()
    user_input = message.text.lower().strip()

    if user_input == "¿que es ipi nacion?":
        bot.send_message(
            message.chat.id, 
            (
                "🏭 Índice de Producción Industrial (IPI)\n\n"
                "El IPI manufacturero es un indicador clave que refleja el rendimiento "
                "del sector industrial en el país. Este índice mide la evolución mensual "
                "de la actividad de diversas ramas de la industria manufacturera, permitiendo "
                "monitorear el comportamiento de sectores como:\n\n"
                "• 🥦 Alimentos\n"
                "• 👗 Textil\n"
                "• 🪵 Maderas\n"
                "• 🧪 Sustancias Químicas\n"
                "• ⛏️ Minerales no metálicos\n"
                "• 🔧 Metales\n\n"
                "🔍 ¿Para qué sirve?\n"
                "Este indicador es utilizado para analizar la evolución del sector industrial, "
                "identificar tendencias económicas y ayudar en la toma de decisiones estratégicas "
                "a nivel empresarial y gubernamental.\n\n"
                "📈 Conocer el IPI permite entender qué sectores están creciendo o decreciendo, "
                "aportando una visión detallada del estado de la industria nacional."
            )
        )
        bot.send_message(message.chat.id, "¿Qué tema quieres saber sobre IPI Nacion?(Escribe Volver al menu principal para salir)")
        bot.register_next_step_handler(message, lambda m: resp_ipi_nacion(m, bot))
    elif user_input == "ultimo valor":
        ultimo_valor_ipi(df, bot, message)
    elif user_input == "ver grafico":
        pedir_sector_ipi(bot, message)
    elif user_input == "consulta personalizada":
        pedir_fecha_personalizada(bot, message)
    elif user_input == "comparar por fechas":
        pedir_fechas_comparacion(bot, message)
    elif user_input == "volver al menu principal":
        bot.send_message(message.chat.id, "Gracias por consultar sobre IPI Nacion.")
        send_menu_principal(bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Opción no válida. Elige nuevamente.")
        bot.register_next_step_handler(message, lambda m: resp_ipi_nacion(m, bot))

#---------------------ULTIMO VALOR-----------------------
def ultimo_valor_ipi(df, bot, message):
    """Muestra el último valor de las variaciones mensuales y anuales del IPI Nacional y sus sectores."""
    ultimo_registro = df.iloc[-1]
    fecha = ultimo_registro['fecha']
    
    mensaje = (
        f"📅 Últimos valores del IPI Nacional - {get_fecha_en_espanol(fecha)}\n\n"
        f"Variaciones Mensuales:\n"
        f"• 🏭 IPI Manufacturero: {ultimo_registro['var_mensual_ipi_manufacturero']:.1f}%\n"
        f"• 🥦 Alimentos {ultimo_registro['var_mensual_alimentos']:.1f}%\n"
        f"• 👗 Textil {ultimo_registro['var_mensual_textil']:.1f}%\n"
        f"• 🪵 Maderas {ultimo_registro['var_mensual_maderas']:.1f}%\n"
        f"• 🧪 Sustancias {ultimo_registro['var_mensual_sustancias']:.1f}%\n"
        f"• ⛏️ Minerales no metálicos {ultimo_registro['var_mensual_min_no_metalicos']:.1f}%\n"
        f"• 🔧 Metales {ultimo_registro['var_mensual_min_metales']:.1f}%\n\n"
        f"Variaciones Anuales\n"
        f"• 🏭 IPI Manufacturero {ultimo_registro['anual_var_mensual_ipi_manufacturero']:.1f}%\n"
        f"• 🥦 Alimentos {ultimo_registro['anual_var_mensual_alimentos']:.1f}%\n"
        f"• 👗 Textil {ultimo_registro['anual_var_mensual_textil']:.1f}%\n"
        f"• 🪵 Maderas {ultimo_registro['anual_var_mensual_maderas']:.1f}%\n"
        f"• 🧪 Sustancias {ultimo_registro['anual_var_mensual_sustancias']:.1f}%\n"
        f"• ⛏️ Minerales no metálicos {ultimo_registro['anual_var_mensual_min_no_metalicos']:.1f}%\n"
        f"• 🔧 Metales {ultimo_registro['anual_var_mensual_min_metales']:.1f}%"
    )
    bot.send_message(message.chat.id, "¿Qué tema quieres saber sobre IPI Nacion?(Escribe Volver al menu principal para salir)")
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

    bot.send_message(
        message.chat.id, 
        "¿Qué sector del IPI Nación quieres graficar? (Escribe 'Volver' para regresar al menú principal)", 
        reply_markup=board
    )
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

    if sector_key == "volver":
        send_menu_ipi_nacion(bot, message)  # Regresar al menú principal
        return

    if sector_key not in valid_sectors:
        bot.send_message(message.chat.id, "Sector no válido. Por favor selecciona uno de la lista.")
        pedir_sector_ipi(bot, message)
        return

    bot.send_message(
        message.chat.id, 
        f"¿Cuántos meses quieres mostrar para {sector}? Ingrese solo el número. (Escribe 'Volver' para regresar al menú anterior)"
    )
    bot.register_next_step_handler(message, lambda m: generar_y_enviar_grafico_ipi(m, bot, valid_sectors[sector_key]))

def generar_y_enviar_grafico_ipi(message, bot, sector):
    """Genera y envía el gráfico del sector seleccionado."""
    try:
        # Verificar si el usuario eligió "Volver"
        if message.text.strip().lower() == "volver":
            pedir_sector_ipi(bot, message)  # Regresar a la selección de sector
            return

        # Validar que el usuario ingresó un número válido de meses
        meses = int(message.text.strip())
        if meses <= 0:
            raise ValueError("El número de meses debe ser mayor que 0.")

        df = read_data_ipi()
        generar_grafico_ipi(df, sector, meses)

        # Enviar el gráfico al usuario
        with open('grafico_ipi.png', 'rb') as foto:
            bot.send_photo(
                message.chat.id, 
                foto, 
                caption=f"Evolución de {sector} - Últimos {meses} meses"
            )
        send_menu_ipi_nacion(bot, message)

    except ValueError:
        bot.send_message(message.chat.id, "Por favor, ingresa un número válido.")
        bot.register_next_step_handler(message, lambda m: generar_y_enviar_grafico_ipi(m, bot, sector))
    except Exception as e:
        bot.send_message(message.chat.id, f"Ocurrió un error inesperado: {str(e)}")

def generar_grafico_ipi(df, sector, meses):
    """Genera el gráfico del sector seleccionado con las variaciones mensuales."""
    # Ordenar los datos por fecha y seleccionar los últimos 'meses' datos
    df = df.sort_values('fecha').tail(meses)

    # Crear la figura y el gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(df['fecha'], df[sector], marker='o', linestyle='-', label=sector)

    # Añadir valores en cada punto
    for i, row in df.iterrows():
        plt.annotate(
            f"{row[sector]:.1f}%", 
            (row['fecha'], row[sector]), 
            textcoords="offset points", 
            xytext=(0, 10), ha='center'
        )

    # Configurar el título y las etiquetas
    plt.title(f'Evolución de {sector} (variación mensual)', fontsize=16)
    plt.xlabel('Fecha')
    plt.ylabel('Variación (%)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Guardar el gráfico como imagen
    plt.savefig('grafico_ipi.png')
    plt.close()


# ------------------ CONSULTA PERSONALIZADA ------------------
def pedir_fecha_personalizada(bot, message):
    """Solicita al usuario una fecha para la consulta personalizada."""
    bot.send_message(
        message.chat.id, 
        "¿Qué fecha deseas consultar? (Ejemplo: marzo 2023)\n\nEscribe *'Volver'* para regresar al menú anterior.",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, lambda m: consultar_fecha_ipi(m, bot))

def consultar_fecha_ipi(message, bot):
    """Consulta y muestra las variaciones para la fecha proporcionada."""
    try:
        texto_usuario = message.text.strip().lower()

        # Verificar si el usuario eligió volver
        if texto_usuario == "volver":
            send_menu_ipi_nacion(bot, message)  # Regresar al menú principal
            return

        # Intentar convertir el texto ingresado en una fecha válida
        fecha_usuario = convertir_a_fecha(texto_usuario)

        if fecha_usuario is None:
            bot.send_message(
                message.chat.id, 
                "Fecha inválida. Usa el formato 'mes año'. Ejemplo: marzo 2023.\nEscribe *'Volver'* para regresar al menú.",
                parse_mode="Markdown"
            )
            pedir_fecha_personalizada(bot, message)  # Volver a pedir la fecha
            return

        # Cargar los datos y buscar la fecha en el DataFrame
        df = read_data_ipi()
        registro = df[df['fecha'] == fecha_usuario]

        if registro.empty:
            bot.send_message(
                message.chat.id, 
                f"No se encontraron datos para la fecha {message.text.strip()}.\nEscribe *'Volver'* para regresar al menú.",
                parse_mode="Markdown"
            )
            pedir_fecha_personalizada(bot, message)  # Volver a pedir la fecha
            return

        # Mostrar los resultados de esa fecha
        mostrar_resultados_fecha(bot, message, registro.iloc[0])

    except Exception as e:
        bot.send_message(message.chat.id, f"Ocurrió un error: {str(e)}")

def convertir_a_fecha(texto):
    """Convierte una entrada de 'mes año' a un objeto datetime."""
    try:
        # Normalizar el texto eliminando tildes y espacios innecesarios
        texto = unidecode.unidecode(texto.strip().lower())
        mes, año = texto.split()

        # Crear una lista de meses sin tildes
        meses_es = [unidecode.unidecode(m.lower()) for m in calendar.month_name if m]

        if mes not in meses_es:
            return None  # Mes no válido

        # Obtener el número del mes
        mes_numero = meses_es.index(mes) + 1  # Ajustar índice

        # Retornar la fecha en formato datetime
        return pd.to_datetime(f"01/{mes_numero}/{año}", format='%d/%m/%Y')

    except (ValueError, IndexError):
        return None  # Devolver None si hay errores

def mostrar_resultados_fecha(bot, message, registro):
    """Muestra los resultados de la fecha seleccionada."""
    fecha = registro['fecha']
    mensaje = (
        f"📅 *Resultados del IPI Nacional para {get_fecha_en_espanol(fecha)}* 📅\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔍 *Variaciones Mensuales*\n"
        f"- 🏭 IPI Manufacturero: {registro['var_mensual_ipi_manufacturero']:.1f}%\n"
        f"- 🥦 Alimentos: {registro['var_mensual_alimentos']:.1f}%\n"
        f"- 👗 Textil: {registro['var_mensual_textil']:.1f}%\n"
        f"- 🪵 Maderas: {registro['var_mensual_maderas']:.1f}%\n"
        f"- 🧪 Sustancias: {registro['var_mensual_sustancias']:.1f}%\n"
        f"- ⛏️ Minerales no metálicos: {registro['var_mensual_min_no_metalicos']:.1f}%\n"
        f"- 🔧 Metales: {registro['var_mensual_min_metales']:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *Variaciones Anuales*\n"
        f"- 🏭 IPI Manufacturero: {registro['anual_var_mensual_ipi_manufacturero']:.1f}%\n"
        f"- 🥦 Alimentos: {registro['anual_var_mensual_alimentos']:.1f}%\n"
        f"- 👗 Textil: {registro['anual_var_mensual_textil']:.1f}%\n"
        f"- 🪵 Maderas: {registro['anual_var_mensual_maderas']:.1f}%\n"
        f"- 🧪 Sustancias: {registro['anual_var_mensual_sustancias']:.1f}%\n"
        f"- ⛏️ Minerales no metálicos: {registro['anual_var_mensual_min_no_metalicos']:.1f}%\n"
        f"- 🔧 Metales: {registro['anual_var_mensual_min_metales']:.1f}%\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    bot.send_message(message.chat.id, mensaje, parse_mode="Markdown")
    send_menu_ipi_nacion(bot, message)  # Volver al menú principal


# ------------------- Comparar por fechas -------------------
def pedir_fechas_comparacion(bot, message):
    """Solicita al usuario las dos fechas para comparar."""
    bot.send_message(
        message.chat.id, 
        "Por favor, ingresa la primera fecha (Ejemplo: marzo 2023).\nEscribe 'Volver' para regresar al menú anterior."
    )
    bot.register_next_step_handler(message, lambda m: obtener_fecha_comparacion_1(m, bot))

def obtener_fecha_comparacion_1(message, bot):
    """Guarda la primera fecha y pide la segunda."""
    texto_usuario = message.text.strip().lower()

    # Verificar si el usuario quiere volver
    if texto_usuario == "volver":
        send_menu_ipi_nacion(bot, message)  # Regresar al menú principal
        return

    fecha_1 = convertir_a_fecha(texto_usuario)

    if fecha_1 is None:
        bot.send_message(
            message.chat.id, 
            "Fecha inválida. Usa el formato 'mes año'. Ejemplo: marzo 2023.\nEscribe 'Volver' para regresar."
        )
        pedir_fechas_comparacion(bot, message)  # Volver a pedir la primera fecha
        return

    bot.send_message(
        message.chat.id, 
        "Ahora ingresa la segunda fecha (Ejemplo: marzo 2024).\nEscribe 'Volver' para regresar al menú anterior."
    )
    bot.register_next_step_handler(message, lambda m: obtener_fecha_comparacion_2(m, bot, fecha_1))

def obtener_fecha_comparacion_2(message, bot, fecha_1):
    """Guarda la segunda fecha y realiza la comparación."""
    texto_usuario = message.text.strip().lower()

    # Verificar si el usuario quiere volver
    if texto_usuario == "volver":
        pedir_fechas_comparacion(bot, message)  # Regresar a la selección de la primera fecha
        return

    fecha_2 = convertir_a_fecha(texto_usuario)

    if fecha_2 is None:
        bot.send_message(
            message.chat.id, 
            "Fecha inválida. Usa el formato 'mes año'. Ejemplo: marzo 2024.\nEscribe 'Volver' para regresar."
        )
        pedir_fechas_comparacion(bot, message)  # Volver a pedir la primera fecha
        return

    df = read_data_ipi()
    realizar_comparacion(bot, message, df, fecha_1, fecha_2)

def convertir_a_fecha(texto):
    """Convierte una entrada de 'mes año' a un objeto datetime."""
    try:
        # Normalizamos la entrada eliminando tildes y manejando minúsculas
        texto = unidecode.unidecode(texto.strip().lower())
        mes, año = texto.split()

        # Crear una lista de meses sin tildes
        meses_es = [unidecode.unidecode(m.lower()) for m in calendar.month_name if m]

        if mes not in meses_es:
            return None  # Mes no válido

        # Obtener el número del mes
        mes_numero = meses_es.index(mes) + 1  # Ajustar porque la lista empieza en 1

        # Retornar la fecha en formato datetime
        return pd.to_datetime(f"01/{mes_numero}/{año}", format='%d/%m/%Y')

    except (ValueError, IndexError):
        return None  # Si hay un error en la conversión, devolvemos None

def realizar_comparacion(bot, message, df, fecha_1, fecha_2):
    """Realiza la comparación entre las dos fechas seleccionadas."""
    registro_1 = df[df['fecha'] == fecha_1]
    registro_2 = df[df['fecha'] == fecha_2]

    if registro_1.empty or registro_2.empty:
        bot.send_message(
            message.chat.id, 
            "⚠️ No se encontraron datos para una o ambas fechas seleccionadas. Inténtalo nuevamente."
        )
        send_menu_ipi_nacion(bot, message)  # Regresar al menú principal
        return

    def calcular_variacion(val1, val2):
        """Calcula la diferencia porcentual entre dos valores."""
        return ((val2 - val1) / abs(val1)) * 100 if val1 != 0 else 0

    mensaje = f"📊 Comparación del IPI Nacional entre {get_fecha_en_espanol(fecha_1)} y {get_fecha_en_espanol(fecha_2)} \n"
    mensaje += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

    # Lista de sectores y sus nombres amigables
    sectores = {
        'var_mensual_ipi_manufacturero': '🏭 IPI Manufacturero',
        'var_mensual_alimentos': '🥦 Alimentos',
        'var_mensual_textil': '👗 Textil',
        'var_mensual_maderas': '🪵 Maderas',
        'var_mensual_sustancias': '🧪 Sustancias',
        'var_mensual_min_no_metalicos': '⛏️ Minerales no metálicos',
        'var_mensual_min_metales': '🔧 Metales'
    }

    # Construir mensaje para cada sector
    for sector, nombre in sectores.items():
        val1 = registro_1[sector].values[0]
        val2 = registro_2[sector].values[0]
        variacion = calcular_variacion(val1, val2)
        tendencia = "📈" if variacion > 0 else "📉" if variacion < 0 else "➡️"

        mensaje += f"- {nombre}: {val1:.1f}% → {val2:.1f}% ({variacion:+.1f}%) {tendencia}\n"

    mensaje += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    mensaje += f"📌 Comparación completa realizada entre {get_fecha_en_espanol(fecha_1)} y {get_fecha_en_espanol(fecha_2)}."

    bot.send_message(message.chat.id, mensaje)
    send_menu_ipi_nacion(bot, message)  # Regresar al menú principal
