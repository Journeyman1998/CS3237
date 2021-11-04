from flask import Flask, send_file
from flask_restful import Resource, Api, reqparse
import werkzeug
import sqlite3

conn = sqlite3.connect('./iot.db', check_same_thread=False)

IMAGE_NAME = "./img/latest.jpg"

get_latest_gesture_sql = """
SELECT * FROM gesture ORDER BY id DESC LIMIT 1;
"""

get_latest_humidity_sql = """
SELECT * FROM humidity ORDER BY id DESC LIMIT 1;
"""

humidityLevel = []

def f(x):
    return abs(-9 * x + 90) + 10

app = Flask(__name__)
api = Api(app)

class Gesture(Resource):
    def get(self):

        # get gesture
        cur = conn.cursor()
        row = conn.execute(get_latest_gesture_sql).fetchone()

        global humidityLevel
        if len(humidityLevel) > 20:
            humidityLevel = []
        humidity = f(len(humidityLevel))
        humidityLevel.append(humidity)

        # get humidity
        cur = conn.cursor()
        humidity = conn.execute(get_latest_humidity_sql).fetchone()[1]

        results = {"id": row[0], "gesture": row[1], "humidity": humidity}
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


api.add_resource(Gesture, '/app')
api.add_resource(Image, '/image')
api.add_resource(UploadImage, '/upload')

if __name__ == "__main__":
    app.run(host="172.31.13.103")