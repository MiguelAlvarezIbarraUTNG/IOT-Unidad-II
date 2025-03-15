import time
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Red-Peter"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_buzzer"
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "postgres/actuators"

# Configuración del Buzzer
BUZZER_PIN = PWM(Pin(27))  # Conectar buzzer pasivo al GPIO 27
BUZZER_PIN.freq(1000)  # Frecuencia inicial (1 kHz)
BUZZER_PIN.duty(0)  # Iniciar apagado

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
        
        # Encender el buzzer (emitir sonido a 1000 Hz)
        BUZZER_PIN.duty(512)  # Valor de 0 a 1023 (512 = volumen medio)
        print("[INFO] Buzzer ENCENDIDO")
        client.publish(MQTT_TOPIC, "Buzzer ENCENDIDO")
        time.sleep(3)  # Mantener sonido 3 segundos

        # Apagar el buzzer
        BUZZER_PIN.duty(0)
        print("[INFO] Buzzer APAGADO")
        client.publish(MQTT_TOPIC, "Buzzer APAGADO")
        time.sleep(3)  # Mantener apagado 3 segundos
    
    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
        time.sleep(5)
