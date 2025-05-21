from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, session
from functools import wraps
import os
import requests
import threading
import secrets
import yaml
import string

app = Flask(__name__)
app.secret_key = secrets.token_hex(32) 

audio_folder = './audio'
os.makedirs(audio_folder, exist_ok=True)



f = open('devices.yaml', 'r')
device_list = yaml.safe_load(f)
f.close()
audio_folder = './audio'

SERVER_BASE_URL = 'https://%s:8443'% (device_list['server'])

tokens = {}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/token', methods=['GET'])
def token():
    ip_addr = request.remote_addr
    if ip_addr in device_list.values():
        alphabet = string.ascii_letters + string.digits
        while True:
            # Generate a random token
            token = ''.join(secrets.choice(alphabet) for i in range(8))
            # Check if the token already exists
            if token not in tokens:
                break
        tokens[token] = ip_addr
        print('request from', ip_addr, 'token', token)
        return jsonify({'token': token}), 200
    else:
        return jsonify({'error': 'Unauthorized'}), 401
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.json.get('token')
        if token in tokens:
            session['logged_in'] = True
            session['device_ip'] = tokens[token]
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'unauthorized'}), 401
    return render_template('login.html')

@app.route('/')
@login_required
def main():
    return render_template('index.html')

@app.route('/devices', methods=['GET'])
@login_required
def get_devices():
    params = {'device_ip': session.get('device_ip')}
    resp = requests.get(f'{SERVER_BASE_URL}/devices', params=params, verify=False)
    return jsonify(resp.json())

@app.route('/record', methods=['POST'])
@login_required
def record():
    payload = request.get_json()
    payload['ip'] = session.get('device_ip')
    resp = requests.post(f'{SERVER_BASE_URL}/record', json=payload, verify=False)
    return resp.text

@app.route('/stop', methods=['POST'])
@login_required
def stop():
    payload = request.get_json()
    payload['ip'] = session.get('device_ip')
    resp = requests.post(f'{SERVER_BASE_URL}/stop', json=payload, verify=False)
    return resp.text

@app.route('/label', methods=['POST'])
@login_required
def label():
    payload = request.get_json()
    resp = requests.post(f'{SERVER_BASE_URL}/label', json=payload, verify=False)
    return resp.text


@app.route('/get-audio/<vin>', methods=['GET'])
@login_required
def get_audio(vin):
    resp = requests.get(f'{SERVER_BASE_URL}/get-audio/{vin}', verify=False)
    return resp.text

@app.route('/play/<audio>', methods=['GET'])
@login_required
def play(audio):
    remote_url = f'{SERVER_BASE_URL}/play/{audio}'
    local_path = os.path.join(audio_folder, audio)
    if os.path.exists(local_path):
        print('Local path already exists')
        return send_file(local_path, as_attachment=True, download_name=audio)
    try:
        # Download remote audio to local path
        with requests.get(remote_url, stream=True, verify=False) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        # Serve the local file
        return send_file(local_path, as_attachment=True, download_name=audio)

    except Exception as e:
        return f'Error downloading file: {str(e)}', 500

    finally:
        # Clean up the local file
        def clean_local():
            if os.path.exists(local_path):
                os.remove(local_path)
        threading.Timer(600, clean_local).start()

@app.route('/delete/<audio>', methods=['GET'])
@login_required
def delete(audio):
    local_path = os.path.join(audio_folder, audio)
    if os.path.exists(local_path):
        os.remove(local_path)
    resp = requests.get(f'{SERVER_BASE_URL}/delete/{audio}', verify=False)
    return resp.text

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=9925, use_reloader=False, ssl_context=('cert.pem', 'key.pem'))