import threading
import time

from cam import Camera
from water import WaterPlant

def main():
    camera = Camera()
    water = WaterPlant()

    t1 = threading.Thread(target=camera.start)
    t2 = threading.Thread(target=water.start)

    t1.start()
    t2.start()

    while True:
        userinput = input("Quit (y/n): ")
        if userinput == 'y':
            exit(0)
        time.sleep(10)


if __name__ == "__main__":
    main()