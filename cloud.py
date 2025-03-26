from flask import Flask, render_template, jsonify, request, send_file
import os
import requests

app = Flask(__name__)

audio_folder = './audio'
os.makedirs(audio_folder, exist_ok=True)

@app.route('/')
def main():
    return render_template('index.html')

SERVER_BASE_URL = 'https://10.94.0.16:8443'

@app.route('/devices', methods=['GET'])
def get_devices():
    resp = requests.get(f'{SERVER_BASE_URL}/devices', verify=False)
    return jsonify(resp.json())

@app.route('/record', methods=['POST'])
def record():
    payload = request.get_json()
    resp = requests.post(f'{SERVER_BASE_URL}/record', json=payload, verify=False)
    return resp.text

@app.route('/stop', methods=['POST'])
def stop():
    payload = request.get_json()
    resp = requests.post(f'{SERVER_BASE_URL}/stop', json=payload, verify=False)
    return resp.text
@app.route('/label', methods=['POST'])
def label():
    payload = request.get_json()
    resp = requests.post(f'{SERVER_BASE_URL}/label', json=payload, verify=False)
    return resp.text


@app.route('/get-audio/<vin>', methods=['GET'])
def get_audio(vin):
    resp = requests.get(f'{SERVER_BASE_URL}/get-audio/{vin}', verify=False)
    return resp.text

@app.route('/play/<audio>', methods=['GET'])
def play(audio):
    remote_url = f'{SERVER_BASE_URL}/play/{audio}'
    local_path = os.path.join(audio_folder, audio)
    if os.path.exists(local_path):
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
        if os.path.exists(local_path):
            os.remove(local_path)

@app.route('/delete/<audio>', methods=['GET'])
def delete(audio):
    os.remove(os.path.join(audio_folder, audio))
    resp = requests.post(f'{SERVER_BASE_URL}/delete/{audio}', verify=False)
    return resp.text

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=9925, use_reloader=False, ssl_context=('cert.pem', 'key.pem'))