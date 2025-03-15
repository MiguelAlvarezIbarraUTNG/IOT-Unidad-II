import time
import network
from machine import ADC, Pin
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "DESKTOP-BVQOQ56 7592"
WIFI_PASSWORD = "Popeye08"

# 🌐 Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_sonido"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"  # Tema para publicar los valores del sensor

# 🚀 Configuración del sensor KY-038 (Analógico)
sensor_pin = ADC(Pin(34))  # Entrada analógica del sensor KY-038 (pin A0)
sensor_pin.width(ADC.WIDTH_10BIT)  # Configura el ancho de bits (10 bits = 0-1023)
sensor_pin.atten(ADC.ATTN_0DB)  # Configura la atenuación (0-3.3V)

# 🔌 Conectar WiFi
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

# 🔄 Conectar a MQTT
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        return None

# 🏁 Bucle principal
conectar_wifi()
client = conectar_mqtt()

while True:
    try:
        # 🔍 Leer sensor (lectura analógica)
        sonido = sensor_pin.read()  # Lee un valor entre 0 y 1023

        # 🚀 Publicar en MQTT
        if client:
            client.publish(MQTT_TOPIC, str(sonido))
            print(f"[INFO] Publicado en {MQTT_TOPIC}: {sonido}")

        # Esperar antes de la siguiente lectura
        time.sleep(2)

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None  # Intentará reconectar en la siguiente iteración
        time.sleep(5)