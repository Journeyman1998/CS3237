import requests
import ast
import time
import pygame
from pygame import mixer

WATER_DURATION = 5
ADDRESS = "http://18.142.17.12:5000/app"

class WaterPlant:
    def __init__(self):
        data = self.getAppData()
        self.id = data['id']
        self.gesture = data['gesture']
        self.humidity = data['humidity']
        self.lowHumidity = data['config']['low_threshold']

        mixer.init() 

    def getAppData(self):
        data = requests.get(ADDRESS, timeout=2)

        if data.status_code == 200:
            data = ast.literal_eval(data.text)
            print(data)
            return data
        else:
            return None

    def start(self):
        while True:
            time.sleep(2)
            data = self.getAppData()

            if self.toStartWaterPlant(data):
                self.waterPlant()
            
            self.updateState(data)
            

    def waterPlant(self):
        print("Play music")
        # sound = mixer.Sound("song.mp3")
        # sound.play(maxtime = WATER_DURATION)
        pygame.mixer.music.load('song.mp3')
        pygame.mixer.music.play(loops=1)

    def updateState(self, data):
        self.id = data['id']
        self.gesture = data['gesture']
        self.humidity = data['humidity']
        self.lowHumidity = data['config']['low_threshold']


    def toStartWaterPlant(self, data):
        newId = data['id']
        newGesture = data['gesture']
        newHumidity = data['humidity']

        if newId != self.id and newGesture == "Water plant" and newHumidity <= self.lowHumidity:
            print("Water plant")
            return True
        else:
            return False
    

if __name__ == "__main__":
    w = WaterPlant()
    w.start()