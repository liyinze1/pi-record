from flask import Flask, send_file, render_template, jsonify, request
import os
from server_utils import *
import time

app = Flask(__name__)

receive_threads = {}

device_list:dict = import_device()

pi_controller = Pi_controller()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/devices', methods=['GET'])
def get_devices():
    response = {}
    for device, ip in device_list.items():
        response[device] = pi_controller.status((ip, 22000))
    return jsonify(response)

@app.route('/record', methods=['POST'])
def record():
    vin = request.get_json('vin')
    device = request.get_json('device')
    print('Request to start recording, device', device, 'vin', vin)
    return 'ok'

@app.route('/stop', methods=['POST'])
def stop():
    vin = request.get_json('vin')
    device = request.get_json('device')
    print('Request to stop recording, device', device, 'vin', vin)
    return 'ok'

@app.route('/shut-down', methods=['POST'])
def shut_down():
    pass

@app.route('/reboot', methods=['POST'])
def reboot():
    pass

@app.route('/report/<vin>/<status>', methods=['GET'])
def report(vin, status):
    return 'ok'

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=8080, use_reloader=False)
    # app.run(host='127.0.0.1', debug=True, port=8000)
    
    