import paho.mqtt.client as mqtt
import sqlite3
from settings import USERNAME, PASSWORD, MQTT_HUMIDITY

conn = sqlite3.connect('./iot.db', check_same_thread=False)

add_humidity_to_db_sql = """
    INSERT INTO humidity(value) VALUES(?);
"""

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to EC2 with result code " + str(rc))
        client.subscribe(MQTT_HUMIDITY)
    else:
        print("Failed to connect. Error code %d." % rc)

def on_message(client,data,msg):
    payload = str(msg.payload, 'utf-8')
    print(f"Message Received: {payload}")
    write_to_db(payload)

def setup():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting...")

    client.connect("localhost")
    client.loop_forever()

def write_to_db(data):
    cur = conn.cursor()
    cur.execute(add_humidity_to_db_sql, (data,))
    conn.commit()

if __name__ == "__main__":
    setup()