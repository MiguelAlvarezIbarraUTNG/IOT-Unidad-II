import time
import network
from machine import Pin
from umqtt.simple import MQTTClient
import onewire, ds18x20

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky001"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

# Configuración del sensor KY-001 (DS18B20 en GPIO 4)
datapin = Pin(4)  
ds_sensor = ds18x20.DS18X20(onewire.OneWire(datapin))

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

# Buscar sensores DS18B20 en el bus 1-Wire
roms = ds_sensor.scan()
if not roms:
    print("[ERROR] No se encontró ningún sensor DS18B20")
    while True:
        time.sleep(1)

while True:
    try:
        if not client:
            client = conectar_mqtt()
            if not client:
                time.sleep(5)
                continue

        # Leer temperatura del KY-001 (DS18B20)
        ds_sensor.convert_temp()
        time.sleep(1)  # Esperar conversión
        temp = ds_sensor.read_temp(roms[0])
        
        print(f"[INFO] Temperatura: {temp:.2f} °C")
        client.publish(MQTT_TOPIC, f"Temperatura: {temp:.2f} °C")

        time.sleep(5)  # Enviar cada 5 segundos
    
    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
        time.sleep(5)
