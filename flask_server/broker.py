import paho.mqtt.client as mqtt
import sys
import sqlite3

sys.path.append("/home/ubuntu/iot/")
from settings import DB_DIR

class MQTT_Broker:

    def write_to_db(self, cmd, payload):
        cur = self.conn.cursor()
        cur.execute(cmd, (payload,))
        self.conn.commit()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to EC2 with result code " + str(rc))
            client.subscribe(self.topic)
        else:
            print("Failed to connect. Error code %d." % rc)

    def on_message(self, client, data, msg):
        payload = str(msg.payload, 'utf-8')
        print(f"Message Received: {payload}")
        self.write_to_db(self.sql_command, payload)

    def on_publish(self, client, userdata, result):
        print("Published")

    def __init__(self, USERNAME=None, PASSWORD=None, HOST_ADDRESS='localhost', SQL_INSTRUC='None', TOPIC='', PUBLISH_MSG=None):
        self.client = mqtt.Client()
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.topic = TOPIC
        self.publish_message = PUBLISH_MSG

        self.conn = sqlite3.connect(DB_DIR, check_same_thread=False)
        self.sql_command = SQL_INSTRUC

        self.client.connect(HOST_ADDRESS)

    def run(self):
        self.client.start_loop() #or loop_forever() ?

    def publish(self):
        self.client.publish(self.topic, self.publish_message)