import machine
import network
import time
from umqtt.simple import MQTTClient

# Configuración de WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_joystick"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors/joystick"

# Pines del Joystick
VRX_PIN = 34  # Eje X
VRY_PIN = 35  # Eje Y
BTN_PIN = 32  # Botón

# Configuración de pines
vrx = machine.ADC(machine.Pin(VRX_PIN))
vry = machine.ADC(machine.Pin(VRY_PIN))
btn = machine.Pin(BTN_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

# Configurar rango del ADC
vrx.atten(machine.ADC.ATTN_11DB)
vry.atten(machine.ADC.ATTN_11DB)

# Conexión a WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print("Conectado a WiFi:", wlan.ifconfig())

connect_wifi()

# Función para conectar a MQTT con reintento
def connect_mqtt():
    global client
    while True:
        try:
            client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
            client.connect()
            print("Conectado a MQTT")
            return
        except OSError:
            print("Error conectando a MQTT, reintentando en 5 segundos...")
            time.sleep(5)

connect_mqtt()

# Valores de referencia
CENTER_TOLERANCE = 600
X_CENTER = vrx.read()
Y_CENTER = vry.read()

while True:
    try:
        x_value = vrx.read()
        y_value = vry.read()
        button_pressed = btn.value()

        message = "Botón Inmóvil"

        if x_value > X_CENTER + CENTER_TOLERANCE:
            message = "+x"
        elif x_value < X_CENTER - CENTER_TOLERANCE:
            message = "-x"
        elif y_value > Y_CENTER + CENTER_TOLERANCE:
            message = "+y"
        elif y_value < Y_CENTER - CENTER_TOLERANCE:
            message = "-y"
        elif button_pressed == 0:
            message = "Botón Presionado"

        client.publish(MQTT_TOPIC, message)
        print("Publicado:", message)

    except OSError as e:
        print("Error MQTT:", e)
        connect_mqtt()  # Reintentar conexión si falla

    time.sleep(0.5)