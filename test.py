
from server_utils import *
import time

device_list:dict = import_device()

pi_controller = Pi_controller()

# time.sleep(1)

response = {}
for device, ip in device_list.items():
    response[device] = pi_controller.status((ip, 23000))