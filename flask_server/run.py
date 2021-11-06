from flask import Flask, send_file
from flask_restful import Resource, Api, reqparse
import werkzeug
import sqlite3
import json

from settings import HOST_ADDRESS, DB_DIR, IMAGE_NAME, CONFIG_DIR

conn = sqlite3.connect(DB_DIR, check_same_thread=False)

get_latest_gesture_sql = """
SELECT * FROM gesture ORDER BY id DESC LIMIT 1;
"""

get_latest_humidity_sql = """
SELECT * FROM humidity ORDER BY id DESC LIMIT 1;
"""

app = Flask(__name__)
api = Api(app)

def read_config():
    with open(CONFIG_DIR, "r") as f:
        data = json.load(f)
    return data

def save_config(config):
    with open(CONFIG_DIR, "w") as f:
        json.dump(config, f)


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

        results = {"id": row[0], "gesture": row[1], "humidity": humidity, "config": config}
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

class UpdateHumidity(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('low_humidity', type=int)
        parse.add_argument('high_humidity', type=int)
        args = parse.parse_args()
        low_humidity = args['low_humidity']
        high_humidity = args['high_humidity']

        config = read_config()
        config["low_threshold"] = low_humidity
        config["high_threshold"] = high_humidity
        save_config(config)


api.add_resource(Gesture, '/app')
api.add_resource(Image, '/image')
api.add_resource(UploadImage, '/upload')
api.add_resource(UpdateHumidity, '/config')

if __name__ == "__main__":
    app.run(host=HOST_ADDRESS)