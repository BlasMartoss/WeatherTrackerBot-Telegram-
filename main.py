#Made by Blas Martos Ortega | Didac Martinez Montferrer
# Importamos los paquetes necesarios para el buen funcionamiento del Bot
import os
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext, CallbackQueryHandler
import requests
import key

# Construimos la instancia del bot para que funcione correctamente mediante la Llave utilizada en la clase "key.py"
app = ApplicationBuilder().token(key.TOKEN).build()
script_directory = os.path.dirname(os.path.realpath(__file__))
# Variables globales que utilizaremos en distintos metodos
city_name = ""
weather_icon = ""

# Metodo general del prograna, en este metodo hacemos un control de errores para la ciudad y devolvemos la opción seleccionada por el usuario
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verifica si el usuario proporcionó una ciudad, en caso de que no, mostramos el siguiente error
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a city after /weather.")
    else:
        # Hacemos que la ciudad sea separada por palabras y espacios.
        global city_name
        city_name=""   
        for word in context.args:
            city_name += word + " "
        # Mediante el metodo getCity podemos obtener el status_code para poder dirigir los errores necesarios    
        city = getCity(city_name)
        if city.status_code != 200:
            if city.status_code == 404:
                # En caso de que la ciudad no haya sido encontrada, mostramos el siguiente error por pantalla y terminal
                print(f"Error: The selected city was not found: {city_name}.")
                await update.message.reply_text(f"Error: The selected city was not found: {city_name}.")
            else:
                # Mostramos los errores por terminal y por el chat mediante el bot mostrando el tipo de error
                print(
                    f"Error: The API request failed with status code {city.status_code}.")
                await update.message.reply_text(f"Error: The API request failed with status code {city.status_code}.")
            return
        # Creamos una array que actuará con las diferentes opciones del menu, de esta forma podemos obtener el clic dado por el usuario, es decir, la seleccion que haya hecho
        keyboard = [
            [
                InlineKeyboardButton("Today", callback_data="today"),
                InlineKeyboardButton("Tomorrow", callback_data="tomorrow"),
                InlineKeyboardButton("5 Days Forecast", callback_data="week")
            ]
        ]
        # Creamos un objeto inLineKeyBoardMarkup con el array keyboard como parametro, de esta manera se mostrará por pantalla
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Este mensaje es mostrado por el bot para que el usuario interprete que debe elegir una de las 3 opciones que surjan
        await update.message.reply_text(f"Which option do you wish to use with the city of {city_name}?", reply_markup=reply_markup)

# Crear el manejador de callback para los botones
async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    global city_name
    # si query es true, es a dir, ha tingut un input, fem el seguent: 
    if query:
        option = query.data
        # Si el usuario accede al botón de today, hacemos lo siguiente
        if option == "today":
            #obtenemos los datos con el metodo weathertoday con city como aprametro
            today = WeatherToday(city_name)
            #utilizamos la variable global para mostrar la imagen mas adelante
            global weather_icon
            # Por ultimo, mostramos al usuario los datos que necesita saber mas una imagen
            await query.message.reply_text("Today's weather is:\n")
            await query.message.reply_text(today)
            await query.message.reply_photo(photo=open(getWeatherImage(weather_icon), 'rb'))
        # En caso de que el usuario le de clicc al botón de tomorrow, hacemos lo siguiente:
        elif option == "tomorrow":
            tomorrow = WeatherTomorrow(city_name)
            await query.message.reply_text("Tomorrow Forecast:  \n")
            await query.message.reply_text(tomorrow)
            await query.message.reply_photo(photo=open(getWeatherImage(weather_icon), 'rb'))
        # En caso de que el usuario le de clic al botón de week, hacemos lo siguiente:
        elif option == "week":
            # Llamamos al metodo WeatherWeek con el nombre de la ciudad por parametro
            week = WeatherWeek(city_name)
            await query.message.reply_text("5 Days Forecast: \n")
            # Mostramso el resultado
            await query.message.reply_text(week )

# Agregar el controlador para los botones 
app.add_handler(CallbackQueryHandler(button_callback))
# Agrega el controlador del comando weather
app.add_handler(CommandHandler("weather", weather))

# Creamos el metodo para el controlador start, mostramos una bienvenida al usuario
async def start(update: Update,context: ContextTypes.DEFAULT_TYPE ):
     await update.message.reply_text("🌦️ Welcome to WeatherTracker Bot 🌦️\n\nWith this bot, you can get weather information for cities all around the world. Simply provide the city's name, and we'll provide you with the current forecast and more meteorological details.\n\nTo check the weather for a specific city, use the following command:\n/weather cityname\n\nFor assistance with available commands, use the following command:\n/help\n\nWhich city are you interested in today?")
# Agrega el controlador del comando /start
app.add_handler(CommandHandler("start", start))

# Creamos el metodo para el controlador help, mostramos los comandos de ayuda
async def help(update: Update,context: ContextTypes.DEFAULT_TYPE ):
     await update.message.reply_text("\nTo check the weather for a specific city, use the following command:\n/weather cityname\n\nFor assistance with available commands, use the following command:\n/help\n")
# Agrega el controlador del comando /help
app.add_handler(CommandHandler("help", help))

# Metodo para obtener una imagen relacionada con el clima de la ciudad.
def getWeatherImage(weather: str):
    # Obtenemos el directorio de la carpeta donde estan las imagenes
    script_directory = os.path.dirname(os.path.realpath(__file__))
    image_folder = os.path.join(script_directory, "images")
    
    #Utilizamos el siguiente hash map para elegir el nombre de la imagen que mostraremos
    weather_images = {
        "Clouds": "clouds.png",
        "Clear": "clear.png",
        "Rain": "rain.png",
        "Sunny": "sunny.png",
        "Snow": "snow.png",
        "Fog": "fog.png",
        "Mist": "mist.png",
        "Thunderstorm": "thunderstorm.png",
    }
    # Devolvemos la ruta de la imagen y la devolvemos con el return
    image_path = os.path.join(image_folder, weather_images.get(weather, None))
    return image_path

#Metodo para poder manejar los errores de la api y acceder a la información.
def getCity(city):
    # url de la api para el tiempo del día
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=490da7806c4f32d1694fbc89dd3d1705&units=metric"
    # Realiza una solicitud GET a la API
    response = requests.get(url)
    return response
# Metodo para obtener el clima meteorlogico del dia actual
def WeatherToday(city):
    # Request a la api.
    response = getCity(city)
    # Utilizamos la variable data para almacenar el json de la variable response.
    msg = response.json()
    # Obtenemos la variable temperatura para utilizarla en un if ternario mas adelante.
    temperature = int(msg['main']['temp'])
    # Variable global para saber el resultado del clima y utilizarlo en la función getWeeatherImage.
    global weather_icon
    weather_icon = (msg['weather'][0]['main'])
    # Todos los datos de la api necesarios son extraidos y almacenados en la variable data.
    data = (f" 🌍 {(msg['name'])} [{(msg['sys']['country'])}] {'🥵' if temperature >= 30 else '😊' if 30>temperature>=15 else '🥶' } \n───────────────────────────────\n🌡️ Current Temperature: {temperature} °C  |  Feels Like: {int(msg['main']['feels_like'])} °C\n💧 Humidity: {(msg['main']['humidity'])}%\n💨 Wind: {int(msg['wind']['speed'])} km/h\n❄️ Minimun Temperature: {int(msg['main']['temp_min'])} °C\n🔥 Maximum Temperature: {int(msg['main']['temp_max'])} °C\n─────────────────────────────── \n{(msg['weather'][0]['main'])}\n")
    # Devolvemos los datos.
    return data + "\n \n"
# Metodo para obtener el pronostico del tiempo de mañana mediante una api 
def WeatherTomorrow(city):
    # Llamamos a la primera api para acceder a la latitud y longitud de la ciudad
    response =  getCity(city)
    msg = response.json()
    lat = msg['coord']['lat']
    lon = msg['coord']['lon']
    global weather_icon
    weather_icon = (msg['weather'][0]['main'])
    # Mediante la primera api obtenemos la latitud y longitud que necesitamos utilizar para la siguiente api: 
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=490da7806c4f32d1694fbc89dd3d1705&units=metric"
    # Obtenemos la respuesta de la api en formato json para trabajar con los datos
    apiAnswer = requests.get(url)
    text = apiAnswer.json()
    # Guardamos todos los elementos de la lista del json 
    list = (text['list'])
    weather_data = []
    # Variable para obtener el nombre de la ciudad y el codigo del pais mediante la primera api.
    city_country = (f" 🌍 {(msg['name'])} [{(msg['sys']['country'])}]\n───────────────────────────────\n")
    #Obtenemos el contenido de la posición 0 en la lista "list", la cual es el pronostico de mañana
    item = list[0]  
    # Alamacenamos en la variable day_data los elementos que mostraremos por pantalla mediante el bot
    day_data = f"\n🌡️ Temperature: {int(item['main']['temp'])} °C   |   Feels Like: {int(item['main']['feels_like'])} °C\n💧 Humidity: {(item['main']['humidity'])}%\n💨 Wind: {(item['wind']['speed'])} km/h\n❄️ Minimun Temperature: {int(item['main']['temp_min'])} °C\n🔥 Maximum Temperature: {int(item['main']['temp_max'])} °C\n📝 Weather Description: {(item['weather'][0]['description'])}\n\n───────────────────────────\n- Weather: {(item['weather'][0]['main'])}"
    # Agregamos los datos del día a la lista
    weather_data.append(day_data) 
    # Separamos los elementos de la lista 
    result = "\n".join(weather_data)
    # Return del nombre de la ciudad i del codigo del pais mas los datos del dia
    return city_country + result 
# Metodo para obtener el pronostico de 5 dias del tiempo de una ciudad mediante una api
def WeatherWeek(city): 
    # Llamamos a la primera api para acceder a la latitud y longitud de la ciudad
    response =  getCity(city)
    msg = response.json()
    lat = msg['coord']['lat']
    lon = msg['coord']['lon']
    # Mediante la primera api obtenemos la latitud y longitud que necesitamos utilizar para la siguiente api: 
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=490da7806c4f32d1694fbc89dd3d1705&units=metric"
    # Obtenemos la respuesta de la api en formato json para trabajar con los datos
    apiAnswer = requests.get(url)
    text = apiAnswer.json()
    # Guardamos todos los elementos de la lista del json 
    list = (text['list'])
    weather_data = []
    # Variable para obtener el nombre de la ciudad y el codigo del pais mediante la primera api.
    city_country = (f" 🌍 {(msg['name'])} [{(msg['sys']['country'])}]\n")
    for i in range(5):
        #Obtenemos el contenido de la posición i en la lista "list"
        item = list[i]  
        # Agregamos el número de día
        day_data = f"\nDay {i + 1}\n" 
        # Alamacenamos en la variable day_data los elementos que mostraremos por pantalla mediante el bot
        day_data += f"\n🌡️ Temperature: {int(item['main']['temp'])} °C   |   Feels Like: {int(item['main']['feels_like'])} °C\n💧 Humidity: {(item['main']['humidity'])}%\n💨 Wind: {(item['wind']['speed'])} km/h\n❄️ Minimun Temperature: {int(item['main']['temp_min'])} °C\n🔥 Maximum Temperature: {int(item['main']['temp_max'])} °C\n📝 Weather Description: {(item['weather'][0]['description'])}\n - Weather: {(item['weather'][0]['main'])}\n───────────────────────────"
        # Agregamos los datos del día a la lista
        weather_data.append(day_data) 
    # Separamos los elementos de la lista 
    result = "\n".join(weather_data)
    # Return del nombre de la ciudad i del codigo del pais mas los datos del dia
    return city_country + result 

app.run_polling()