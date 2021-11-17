import paho.mqtt.client as mqtt
import sys
import sqlite3

sys.path.append("/home/ubuntu/iot/")
from settings import DB_DIR


def write_to_db(conn, cmd, payload):
    conn.execute(cmd, (payload,))
    conn.commit()

def get_connect(topic):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to EC2 with result code " + str(rc))

            if topic != None:
                client.subscribe(topic)
                print(f"Subscribed to {topic}\n")
        else:
            print("Failed to connect. Error code %d." % rc)
    
    return on_connect

def get_message(conn, sql_command):
    def on_message(client, data, msg):
        payload = str(msg.payload, 'utf-8')
        print(f"Message Received: {payload}")
        write_to_db(conn, sql_command, payload)
    
    return on_message

class MQTT_Broker:

    def on_publish(self, client, userdata, result):
        print("Published")

    def __init__(self, USERNAME=None, PASSWORD=None, HOST_ADDRESS='localhost', SQL_INSTRUC=None, TOPIC=None):
        self.client = mqtt.Client()
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.conn = sqlite3.connect(DB_DIR, check_same_thread=False)

        self.client.on_connect = get_connect(TOPIC)
        self.client.on_message = get_message(self.conn, SQL_INSTRUC)
        self.client.on_publish = self.on_publish

        self.client.connect(HOST_ADDRESS)

    def run(self):
        self.client.loop_start() #or loop_forever() ?

    def publish(self, topic, message):
        self.client.publish(topic, message)