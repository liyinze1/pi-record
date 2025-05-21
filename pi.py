from flask import Flask, jsonify, request
from pi_utils import *

pi_recorder = Pi_recorder()

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def status():
    
    return jsonify({
        'status': pi_recorder.status(),
        'mode': pi_recorder.mode(),
        'mode_verbose': pi_recorder.mode_verbose(),
    }), 200

@app.route('/record', methods=['POST'])
def record():
    '''Start recording with an integer parameter port.'''
    ip = request.remote_addr
    data = request.get_json()
    port = data['port']
    protocol = data['protocol']
    test = data['test']
    print(data)
    return jsonify({
        'status': pi_recorder.record(ip, port, protocol, test),
    }), 200
    
@app.route('/stop', methods=['POST'])
def stop():
    '''Stop recording.'''
    return jsonify({
        'status': pi_recorder.stop(),
    }), 200

if __name__ == '__main__':
    # pi_recorder = Pi_recorder()
    app.run(host='0.0.0.0', port=22000, debug=True, use_reloader=False, ssl_context=('cert.pem', 'key.pem'))
    
