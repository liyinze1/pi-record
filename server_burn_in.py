from server_utils import *
import time
import threading
from datetime import datetime

receive_threads = {str: Receive}

db = VehicleDatabase()

port_controller = Port_controller()

pi_controller = Pi_controller()

device_ip = '10.94.0.33'

vin = 'tcp_test'

def record():
        
    port = port_controller.get_port()
    
    if pi_controller.record(device_ip, port, protocol='tcp', test=True) == 'recording':
        print('trying to start receiving...')
        receive = Receive(vin, port, protocol='tcp')
        receive_threads[vin] = receive
        return 'recording...'
    # else:
    #     time.sleep(10)
    else:
        port_controller.return_port(port)
        return 'failed to start recording'

def stop():
    if vin in receive_threads:
        receive_threads[vin].stop()
        port = receive_threads.pop(vin).port
        port_controller.return_port(port)
        
    if pi_controller.stop(device_ip) == 'stopped':
        print('trying to stop recording...')
        return 'stopped'
    else:
        return 'failed to stop recording'
    

def log(msg):
    msg = datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + '\t' + msg + '\n'
    print(msg)
    with open('log.txt', 'a') as f:
        f.write(msg)


def record_cycle():
    time.sleep(10)
    while True:
        log(record())
        time.sleep(130)
        log(stop())
        
        time.sleep(400)
        
        # if datetime.now().minute % 10 == 0:
        #     print('it is the time to start...')
        #     log(record())
        #     time.sleep(130)
        #     log(stop())
        # else:
        #     time.sleep(10)
            # print('not yet started\r')
    
def status_cycle():
    while True:
        status = pi_controller.status(device_ip)
        log('status: ' + status)
        time.sleep(30)

threading.Thread(target=status_cycle).start()
threading.Thread(target=record_cycle).start()