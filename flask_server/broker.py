import paho.mqtt.client as mqtt
import sys
import sqlite3

sys.path.append("/home/ubuntu/iot/")
from settings import DB_DIR

class MQTT_Broker:

    def write_to_db(self, cmd, payload):
        self.conn.execute(cmd, (payload,))
        self.conn.commit()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to EC2 with result code " + str(rc))

            if self.topic != None:
                client.subscribe(self.topic)
                print(f"Subscribed to {self.topic}\n")
        else:
            print("Failed to connect. Error code %d." % rc)

    def on_message(self, client, data, msg):
        payload = str(msg.payload, 'utf-8')
        print(f"Message Received: {payload}")
        self.write_to_db(self.sql_command, payload)

    def on_publish(self, client, userdata, result):
        print("Published")

    def __init__(self, USERNAME=None, PASSWORD=None, HOST_ADDRESS='localhost', SQL_INSTRUC=None, TOPIC=None):
        self.client = mqtt.Client()
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.topic = TOPIC
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish

        self.conn = sqlite3.connect(DB_DIR, check_same_thread=False)
        self.sql_command = SQL_INSTRUC

        self.client.connect(HOST_ADDRESS)

    def run(self):
        self.client.loop_start() #or loop_forever() ?

    def publish(self, topic, message):
        self.client.publish(topic, message)