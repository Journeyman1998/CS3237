from flask import Flask, send_file
from flask_restful import Resource, Api, reqparse
import werkzeug
import sqlite3
import json

import sys
from flask_server.broker import MQTT_Broker
sys.path.append("/home/ubuntu/iot/")
sys.path.append("/home/ubuntu/iot/flask_server")
from settings import HOST_ADDRESS, DB_DIR, IMAGE_NAME, CONFIG_DIR, USERNAME, PASSWORD
from broker import MQTT_Broker

conn = sqlite3.connect(DB_DIR, check_same_thread=False)

get_latest_gesture_sql = """
SELECT * FROM gesture ORDER BY id DESC LIMIT 1;
"""

get_latest_humidity_sql = """
SELECT * FROM humidity ORDER BY id DESC LIMIT 1;
"""

get_latest_intensity_sql = """
SELECT * FROM intensity ORDER BY id DESC LIMIT 1;
"""


app = Flask(__name__)
api = Api(app)
record_gesture_broker = MQTT_Broker(USERNAME, PASSWORD, HOST_ADDRESS, None, TOPIC="aegis/start_gesture", PUBLISH_MSG="Trigger gesture record")
record_gesture_broker.run()

def read_config():
    with open(CONFIG_DIR, "r") as f:
        data = json.load(f)
    return data

def save_config(config):
    with open(CONFIG_DIR, "w") as f:
        json.dump(config, f)
    print("Saved")

class Gesture(Resource):
    def get(self):

        # get gesture
        cur = conn.cursor()
        row = conn.execute(get_latest_gesture_sql).fetchone()

        # get humidity
        cur = conn.cursor()
        humidity = conn.execute(get_latest_humidity_sql).fetchone()[1]

        # get config
        config = read_config()

        cur = conn.cursor()
        intensity = conn.execute(get_latest_intensity_sql).fetchone()[1]

        results = {"id": row[0], "gesture": row[1], "humidity": humidity, "intensity": intensity, "config": config}
        print(results)
        return results


class Image(Resource):
    def get(self):
        return send_file(IMAGE_NAME, mimetype='image/jpg')

class UploadImage(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parse.parse_args()
        image_file = args['file']
        image_file.save(IMAGE_NAME)

class Action(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('action', type=str)
        parse.add_argument('payload', type=dict)
        args = parse.parse_args()

        action = args['action']

        if action == 'update_threshold':
            threshold_parser = reqparse.RequestParser()
            threshold_parser.add_argument('low', type=int, location=('payload',))
            threshold_parser.add_argument('high', type=int, location=('payload',))

            low_humidity = args['low']
            high_humidity = args['high']

            config = read_config()
            config["low_threshold"] = low_humidity
            config["high_threshold"] = high_humidity

            save_config(config)
        
        elif action == 'record_gesture':
            record_gesture_broker.publish()


api.add_resource(Gesture, '/app')
api.add_resource(Image, '/image')
api.add_resource(UploadImage, '/upload')
api.add_resource(Action, '/action')

if __name__ == "__main__":
    app.run(host=HOST_ADDRESS)