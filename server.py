from flask import Flask, render_template, jsonify, request
import os
from server_utils import *
import time

app = Flask(__name__)

receive_threads = {}

device_list:dict = import_device()

pi_controller = Pi_controller(port=22001)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/devices', methods=['GET'])
def get_devices():
    response = {}
    for device, addr in device_list.items():
        status = pi_controller.status(addr)
        if status == None:
            response[device] = 'offline'
        else:
            response[device] = status.decode('ascii')
    return jsonify(response)

@app.route('/record', methods=['POST'])
def record():
    vin = request.get_json('vin')
    device = request.get_json('device')
    pi_controller.record(device_list[device])
    print('Request to start recording, device', device, 'vin', vin)
    return 'ok'

@app.route('/stop', methods=['POST'])
def stop():
    vin = request.get_json('vin')
    device = request.get_json('device')
    pi_controller.stop(device_list[device])
    print('Request to stop recording, device', device, 'vin', vin)
    return 'ok'

@app.route('/label', methods=['POST'])
def label():
    vin = request.get_json('vin')
    device = request.get_json('device')
    opt = request.get_json('label')
    return 'ok'

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=8080, use_reloader=False)
    # app.run(host='127.0.0.1', debug=True, port=8000)
    
    