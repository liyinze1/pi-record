from flask import Flask, jsonify, request
from pi_utils import *

app = Flask(__name__)

pi_recorder = Pi_recorder()

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': pi_recorder.status(),
    }), 200

@app.route('/record', methods=['POST'])
def record():
    '''Start recording with an integer parameter port.'''
    ip = request.remote_addr
    data = request.get_json()
    port = data['port']
    return jsonify({
        'status': pi_recorder.record(ip, port),
    }), 200
    
@app.route('/stop', methods=['POST'])
def stop():
    '''Stop recording.'''
    return jsonify({
        'status': pi_recorder.stop(),
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=22000, debug=True)
