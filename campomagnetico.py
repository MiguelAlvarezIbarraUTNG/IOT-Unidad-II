import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky024"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

# Configuración del KY-024
DO_PIN = Pin(18, Pin.IN)   # Salida digital (Detecta presencia de campo magnético)
AO_PIN = ADC(Pin(34))      # Salida analógica (Mide intensidad del campo magnético)
AO_PIN.atten(ADC.ATTN_11DB)  # Configurar ADC para rango de 0-3.3V

# Conectar WiFi
def conectar_wifi():
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 10
    while not sta_if.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    
    if sta_if.isconnected():
        print("\n[INFO] WiFi Conectada!")
        print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")
    else:
        print("\n[ERROR] No se pudo conectar a WiFi")

# Conectar a MQTT
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        return None

# Iniciar conexiones
conectar_wifi()
client = conectar_mqtt()

while True:
    try:
        if not client:
            client = conectar_mqtt()
            if not client:
                time.sleep(5)
                continue
        
        # Leer datos del sensor KY-024
        estado_magnetico = DO_PIN.value()  # 1 = No hay campo, 0 = Campo detectado
        intensidad_magnetica = AO_PIN.read()  # Valor de 0 a 4095 en ESP32

        # Mostrar datos en consola
        print(f"[INFO] Estado Magnético: {'Detectado' if estado_magnetico == 0 else 'No Detectado'}")
        print(f"[INFO] Intensidad Magnética: {intensidad_magnetica}")

        # Publicar en MQTT
        client.publish(MQTT_TOPIC, f"Estado Magnético: {'Detectado' if estado_magnetico == 0 else 'No Detectado'}")
        client.publish(MQTT_TOPIC, f"Intensidad Magnética: {intensidad_magnetica}")

        time.sleep(3)  # Enviar datos cada 3 segundos
    
    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
        time.sleep(5)
