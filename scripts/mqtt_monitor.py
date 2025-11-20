import time
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883


def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with rc={rc}")
    client.subscribe("#")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
    except Exception:
        payload = str(msg.payload)
    print(f"[{time.strftime('%H:%M:%S')}] {msg.topic} -> {payload}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

print("Listening for MQTT messages... Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping monitor (user requested)")
finally:
    client.loop_stop()
    client.disconnect()
    print("Monitor finished")
