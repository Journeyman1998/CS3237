import paho.mqtt.client as mqtt
from settings import DB_DIR, MQTT_GESTURE_RESULTS, USERNAME, PASSWORD
import sqlite3

HOST_ADDRESS = "localhost"

conn = sqlite3.connect(DB_DIR, check_same_thread=False)

add_gesture_to_db_sql = """
    INSERT INTO gesture(gesture_type) VALUES(?);
"""

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to EC2 with result code " + str(rc))
        client.subscribe(MQTT_GESTURE_RESULTS)
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

    client.connect(HOST_ADDRESS)
    client.loop_forever()

def write_to_db(gesture):
    cur = conn.cursor()
    cur.execute(add_gesture_to_db_sql, (gesture,))
    conn.commit()

if __name__ == "__main__":
    setup()