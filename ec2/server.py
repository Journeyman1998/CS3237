import paho.mqtt.client as mqtt
import numpy as np
import json
import tensorflow as tf
from keras.models import load_model
from tensorflow.python.keras.backend import set_session


USERNAME = "aegis"
PASSWORD = "aegis2021"
gesturetype = ["Water plant", "Swipe"]

MODEL_NAME = '/home/ubuntu/model'
session = tf.compat.v1.Session(graph=tf.compat.v1.Graph())

with session.graph.as_default():
    set_session(session)
    model = load_model(MODEL_NAME)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))
    client.subscribe("aegis/gesture")
    print("Listening")

def classify_gesture(data):
    print("Start classifying")
    with session.graph.as_default():
        set_session(session)
        prediction = model.predict(data)
        index = np.argmax(prediction) # dict of gesture index must also put inside MQTT integrated cc2650_manual_read.py file
    print("Done.")

    gesture = gesturetype[index]
    return gesture


def on_message(client, userdata, message):
    data = json.loads(message.payload)
    data = np.array(data)
    data = np.expand_dims(data, axis=0)
    result = classify_gesture(data)
    print(f"Gesture detected: {result}")

    client.publish("aegis/gesture_results", result)

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()