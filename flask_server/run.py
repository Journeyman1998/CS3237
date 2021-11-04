from flask import Flask
from flask_restful import Resource, Api
import sqlite3

conn = sqlite3.connect('./iot.db', check_same_thread=False)

get_latest_gesture_sql = """
SELECT * FROM gesture ORDER BY id DESC LIMIT 1;
"""

humidityLevel = []

def f(x):
    return abs(-9 * x + 90) + 10

app = Flask(__name__)
api = Api(app)

class Gesture(Resource):
    def get(self):
        global humidityLevel
        cur = conn.cursor()
        row = conn.execute(get_latest_gesture_sql).fetchone()
        if len(humidityLevel) > 20:
            humidityLevel = []
        humidity = f(len(humidityLevel))
        humidityLevel.append(humidity)
        results = {"id": row[0], "gesture": row[1], "humidity": humidity}
        print(results)
        return results


class Image(Resource):
    def get(self):
        return {'hello': 'world'}


class PlantData(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(Gesture, '/app')
api.add_resource(Image, '/image')
api.add_resource(PlantData, '/plant')

if __name__ == "__main__":
    app.run(host="172.31.13.103")