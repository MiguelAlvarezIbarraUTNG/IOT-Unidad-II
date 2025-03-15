import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky040"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/sensors"

# Pines del Encoder KY-040
CLK = Pin(32, Pin.IN, Pin.PULL_UP)  # Pin CLK (cambio de estado)
DT = Pin(33, Pin.IN, Pin.PULL_UP)   # Pin DT (dirección del giro)
SW = Pin(35, Pin.IN, Pin.PULL_UP)   # Pin SW (botón del encoder)

# Variable para almacenar el conteo del encoder
contador = 0

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

# Manejo de interrupciones para el encoder
def rotacion_encoder(pin):
    global contador
    if DT.value() != CLK.value():
        contador += 1  # Giro a la derecha
    else:
        contador -= 1  # Giro a la izquierda
    print(f"[INFO] Contador: {contador}")
    client.publish(MQTT_TOPIC, f"Contador: {contador}")

# Manejo del botón del encoder
def presion_boton(pin):
    print("[INFO] Botón Presionado")
    client.publish(MQTT_TOPIC, "Botón Presionado")

# Configurar interrupciones
CLK.irq(trigger=Pin.IRQ_FALLING, handler=rotacion_encoder)
SW.irq(trigger=Pin.IRQ_FALLING, handler=presion_boton)

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
        time.sleep(0.1)  # Pequeña pausa para estabilidad
    
    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
        time.sleep(5)
