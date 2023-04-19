import led
import time

pixels = led.Pixels()

pixels.wakeup()
time.sleep(10)
pixels.off()