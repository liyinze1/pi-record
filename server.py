from flask import Flask, render_template, jsonify, request, send_file
import os
from server_utils import *
import time

app = Flask(__name__)

receive_threads = {str: Receive}

db = VehicleDatabase()

port_controller = Port_controller()

pi_controller = Pi_controller()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/devices', methods=['GET'])
def get_devices():
    response = {}
    for device, addr in device_list.items():
        status = pi_controller.status(addr)
        response[device] = status
    return jsonify(response)

@app.route('/record', methods=['POST'])
def record():
    data = request.get_json()
    vin = data['vin']
    device = data['device']
    if 'protocol' in data:
        protocol = data['protocol']
    else:
        protocol = 'rtp'
    print('Request to start recording, device', device, 'vin', vin)
    port = port_controller.get_port()
    
    if pi_controller.record(device_list[device], port, protocol) == 'recording':
        print('trying to start receiving...')
        receive = Receive(vin, port, protocol)
        receive_threads[vin] = receive
        return 'recording...'
    else:
        port_controller.return_port(port)
        return 'failed to start recording'

@app.route('/stop', methods=['POST'])
def stop():
    data = request.get_json()
    vin = data['vin']
    device = data['device']
    print('Request to stop recording, device', device, 'vin', vin)
    pi_controller.stop(device_list[device])
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
    os.system('rm -f %s' % os.path.join(audio_folder, audio))
    return 'deleted'

if __name__ == '__main__':
    app.run(host='10.94.0.16', debug=True, port=443, use_reloader=False, ssl_context=('cert.pem', 'key.pem'))
    # app.run(host='127.0.0.1', debug=True, port=8000)