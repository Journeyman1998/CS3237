import paho.mqtt.client as mqtt
import json

USERNAME = "aegis"
PASSWORD = "aegis2021"
GESTURE = "aegis/gesture"
RESULTS = "aegis/gesture_results"
HOST_ADDRESS = "18.142.17.12" #"54.179.127.217"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to EC2 with result code " + str(rc))
    else:
        print("Failed to connect. Error code %d." % rc)

def on_message(client,data,msg):
    payload = str(msg.payload, 'utf-8')
    print(f"Message Received: {payload}")

def setup():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    print("Connecting...")

    client.connect(HOST_ADDRESS)
    client.loop_start()

    return client

def send_data(client, data):
    mqtt_data = json.dumps(data)
    client.publish(GESTURE, mqtt_data)
    print("Motion data published!")

