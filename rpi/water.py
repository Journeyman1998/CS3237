import requests
import ast
import time

ADDRESS = "http://18.142.17.12:5000/app"

def getAppData():
    data = requests.get(ADDRESS, timeout=2)

    if data.status_code == 200:
        data = ast.literal_eval(data.text)
        return data
    else:
        return None


def startWaterPlant(data):
    newId = data['id']
    newGesture = data['gesture']
    newHumidity = data['humidity']

    if newId != id and newGesture == "Water plant" and newHumidity:

def main():

    # initialise state
    data = getAppData()
    id = data['id']
    gesture = data['gesture']
    humidity = data['humidity']

    while True:
        time.sleep(2)
        data = getAppData()

        if startWaterPlant(data): 