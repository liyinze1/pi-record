from flask import Flask, render_template, jsonify, request, send_file
import os
import requests
import tempfile

app = Flask(__name__)

audio_folder = './audio'

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
    try:
        # Download remote audio to a temp file
        with requests.get(remote_url, stream=True, verify=False) as r:
            r.raise_for_status()
            suffix = os.path.splitext(audio)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                tmp_path = tmp.name

        # Send the temp file to the client
        return send_file(tmp_path, as_attachment=True, download_name=audio)

    except Exception as e:
        return f'Error downloading file: {str(e)}', 500
    finally:
        # Clean up temp file after sending
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.route('/delete/<audio>', methods=['GET'])
def delete(audio):
    resp = requests.post(f'{SERVER_BASE_URL}/delete/{audio}', verify=False)
    return resp.text

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=9925, use_reloader=False, ssl_context=('cert.pem', 'key.pem'))