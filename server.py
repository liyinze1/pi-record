from flask import Flask, render_template, jsonify, request, send_file
import os
from server_utils import *
import time

app = Flask(__name__)

receive_threads = {str: Receive}

db = VehicleDatabase()

port_controller = Port_controller()

pi_controller = Pi_controller()

@app.route('/devices', methods=['GET'])
def get_devices():
    # response = {}
    # for device, addr in device_list.items():
    #     status = pi_controller.status(addr)
    #     response[device] = status
    device_ip = request.args.get('device_ip', default='', type=str)
    return pi_controller.status(device_ip)

@app.route('/record', methods=['POST'])
def record():
    data = request.get_json()
    vin = data['vin']
    dest = data['ip']
    if 'protocol' in data:
        protocol = data['protocol']
    else:
        protocol = 'rtp'
    print('Request to start recording, device', dest, 'vin', vin)
    port = port_controller.get_port()
    
    if protocol == 'rtp':
        # start recording before the receving thread
        if pi_controller.record(dest, port, protocol) == 'recording':
            print('trying to start receiving...')
            receive = Receive(vin, port, protocol)
            receive_threads[vin] = receive
            return 'recording...'
        else:
            port_controller.return_port(port)
            return 'failed to start recording'
    elif protocol == 'tcp':
        # start the receving thread before recording
        receive = Receive(vin, port, protocol)
        if pi_controller.record(dest, port, protocol) == 'recording':
            print('trying to start receiving...')
            receive_threads[vin] = receive
            return 'recording...'
        else:
            receive.stop()
            port_controller.return_port(port)
            return 'failed to start recording'

@app.route('/stop', methods=['POST'])
def stop():
    data = request.get_json()
    vin = data['vin']
    dest = data['ip']
    print('Request to stop recording, device', dest, 'vin', vin)
    pi_controller.stop(dest)
    if vin in receive_threads:
        receive_threads[vin].stop()
        port = receive_threads.pop(vin).port
        port_controller.return_port(port)
    return 'stopped, please select label'

@app.route('/label', methods=['POST'])
def label():
    data = request.get_json()
    vin = data['vin']
    opt = data['label']
    db.update(vin, opt)
    return 'ok'


@app.route('/get-audio/<vin>', methods=['GET'])
def get_audio(vin):
    return get_audio_filename(vin)

@app.route('/play/<audio>', methods=['GET'])
def play(audio):
    return send_file(os.path.join(audio_folder, audio), as_attachment=True)

@app.route('/delete/<audio>', methods=['GET'])
def delete(audio):
    os.remove(os.path.join(audio_folder, audio))    
    return 'deleted'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8443, use_reloader=False, ssl_context=('cert.pem', 'key.pem'))
    # app.run(host='127.0.0.1', debug=True, port=8000)