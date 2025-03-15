import time
import network
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_mq135"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

# Configuración del sensor MQ-135
sensor = ADC(Pin(34))  # Conectar la señal del MQ-135 al pin 34
sensor.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V

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
        
        # Leer el valor del sensor MQ-135
        lectura = sensor.read()
        
        # Convertir el valor a porcentaje de calidad del aire
        calidad_aire = (lectura / 4095) * 100  # Escala de 0 a 100%
        
        # Clasificación de calidad del aire
        if calidad_aire < 20:
            estado = "EXCELENTE"
        elif calidad_aire < 40:
            estado = "BUENA"
        elif calidad_aire < 60:
            estado = "REGULAR"
        elif calidad_aire < 80:
            estado = "MALA"
        else:
            estado = "MUY MALA"

        mensaje = f"Calidad del aire: {calidad_aire:.2f}% - {estado}"
        print(f"[INFO] {mensaje}")

        # Publicar en MQTT
        client.publish(MQTT_TOPIC, mensaje)
        
        time.sleep(5)  # Esperar 5 segundos antes de la próxima lectura
    
    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
        time.sleep(5)
