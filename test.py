import led
import time

pixels = led.Pixels()

if __name__ == '__main__':
    while True:

        try:
            pixels.speak()
            time.sleep(3)
        except KeyboardInterrupt:
            break


    pixels.off()
    time.sleep(1)