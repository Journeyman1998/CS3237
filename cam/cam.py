import pygame
import pygame.camera
import requests
import time

DELAY = 15 # seconds

pygame.camera.init()
all_cameras = pygame.camera.list_cameras() #Camera detected or not
cam = pygame.camera.Camera(all_cameras[0],(640,480))
cam.start()

while True:
    time.sleep(1)
    img = cam.get_image()
    print("Picture taken")
    pygame.image.save(img,"latest.jpg")
    url = 'http://18.142.17.12:5000/upload'
    requests.post(url, files={'file': open("latest.jpg", "rb")})
    print("Picture sent\n")
    time.sleep(DELAY)