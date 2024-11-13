from server_utils import *
import time
import threading

receive_threads = {str: Receive}

db = VehicleDatabase()

port_controller = Port_controller()

pi_controller = Pi_controller()

device_ip = '172.27.201.235'

vin = 'test'

def record():
        
    port = port_controller.get_port()
    
    
    if pi_controller.test(device_ip, port) == 'recording':
        print('trying to start receiving...')
        receive = Receive(vin, port)
        receive_threads[vin] = receive
        return 'recording...'
    else:
        port_controller.return_port(port)
        return 'failed to start recording'

def stop():
    if pi_controller.stop(device_ip) == 'stopped':
        print('trying to stop recording...')
        if vin in receive_threads:
            receive_threads[vin].stop()
            port = receive_threads.pop(vin).port
            port_controller.return_port(port)
        return 'stopped'
    else:
        return 'failed to stop recording'
    

def log(msg):
    msg = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + '\t' + msg + '\n'
    print(msg)
    with open('log.txt', 'a') as f:
        f.write(msg)


def record_cycle():
    while True:
        log(record())
        time.sleep(150)
        log(stop())
        time.sleep(180)
    
def status_cycle():
    while True:
        status = pi_controller.status(device_ip)
        log('status: ' + status)
        time.sleep(30)
    

threading.Thread(target=status_cycle).start()
threading.Thread(target=record_cycle).start()