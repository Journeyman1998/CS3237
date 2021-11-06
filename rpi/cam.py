import pygame
import pygame.camera
import requests
import time

DELAY = 15 # seconds
HOST_ADDRESS = 'http://18.142.17.12:5000/upload'
class Camera:
    def __init__(self):
        pygame.camera.init()
        all_cameras = pygame.camera.list_cameras() #Camera detected or not
        self.cam = pygame.camera.Camera(all_cameras[0],(640,480))
        self.cam.start()

    def start(self):
        while True:
            time.sleep(1)
            img = self.cam.get_image()
            print("Picture taken")
            pygame.image.save(img,"latest.jpg")
            requests.post(HOST_ADDRESS, files={'file': open("latest.jpg", "rb")})
            print("Picture sent\n")
            time.sleep(DELAY)