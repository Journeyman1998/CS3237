import paho.mqtt.client as mqtt
import json

USERNAME = "aegis"
PASSWORD = "aegis2021"
HOST_ADDRESS = "18.142.17.12" #"54.179.127.217"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to EC2 with result code " + str(rc))
    else:
        print("Failed to connect. Error code %d." % rc)

def on_message(client,data,msg):
    payload = str(msg.payload, 'utf-8')

    if client.sub_callback != None:
        client.sub_callback(client.sub_callback_args)

    print(f"Message Received: {payload}")

def setup(host_address=HOST_ADDRESS, username=USERNAME, password=PASSWORD, sub_topic=None, sub_callback=None, sub_callback_args=None):
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    print("Connecting...")

    client.connect(HOST_ADDRESS)

    if sub_topic != None:
        client.subscribe(sub_topic)

    client.sub_callback = sub_callback
    client.sub_callback_args = sub_callback_args

    client.loop_start()

    return client

def send_data(client, data, topic):
    mqtt_data = json.dumps(data)
    client.publish(topic, mqtt_data)
    print("Data published!")


