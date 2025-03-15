from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "DESKTOP-BVQOQ56 7592"
WIFI_PASSWORD = "Popeye08"

# 🌐 Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_inclinacion"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC_SENSOR = "postgres/sensors"  # Publicará solo 1 o 0

# 🚀 Configuración de pines
sensor_pin = Pin(4, Pin.IN)   # Entrada digital del sensor KY-027
led_pin = Pin(16, Pin.OUT)    # Salida para el LED

# 📶 Conexión WiFi
def conectar_wifi():
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)

    print("\n[INFO] WiFi Conectada!")
    print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")

# 🔄 Conexión MQTT
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        return None

# 🔌 Conectar WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

# 🏁 Bucle principal
while True:
    try:
        # 📡 Verificar WiFi
        if not network.WLAN(network.STA_IF).isconnected():
            print("[ERROR] WiFi desconectado, reconectando...")
            conectar_wifi()
            client = conectar_mqtt()

        # 🔄 Verificar conexión MQTT
        if client is None:
            print("[ERROR] MQTT desconectado, reconectando...")
            client = conectar_mqtt()
            time.sleep(5)
            continue

        # 🔍 Leer sensor
        estado_sensor = sensor_pin.value()  # 1 = Inclinado, 0 = Normal
        led_pin.value(estado_sensor)  # LED refleja el estado

        # 📡 Publicar en MQTT
        mensaje = str(estado_sensor)  # Envía "1" o "0"
        client.publish(MQTT_TOPIC_SENSOR, mensaje)
        print(f"[INFO] Publicado en {MQTT_TOPIC_SENSOR}: {mensaje}")

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None  # Intentará reconectar en la siguiente iteración

    time.sleep(2)  # Esperar 2 segundos antes de la siguiente lectura