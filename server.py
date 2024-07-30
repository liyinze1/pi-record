from flask import Flask, send_file, render_template
import utils
import os

app = Flask(__name__)

receive_threads = {}

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/record/<vin>', methods=['GET'])
def record(vin):
    pass

@app.route('/test-loss-rate', methods=['GET'])
def test_loss_rate():
    pass

@app.route('/stop', methods=['GET'])
def stop():
    pass

@app.route('/shut-down', methods=['POST'])
def shut_down():
    pass

@app.route('/reboot', methods=['POST'])
def reboot():
    pass

@app.route('/report/<vin>/<status>', methods=['GET'])
def report(vin, status):
    return 'ok'

@app.route('/check-last-audio/<position>', methods=['GET'])
def check_last_audio(position):
    if position == 'pi':
        return utils.check_last_audio()
    else:
        return utils.check_last_audio_server()

@app.route('/delete-last-audio/<position>/<audio>', methods=['GET'])
def delete_last_audio(position, audio):
    if position == 'pi':
        return utils.delete_last_audio(audio)
    else:
        return utils.delete_last_audio_server(audio)

@app.route('/check-update', methods=['GET'])
def check_update():
    return utils.git_status()

@app.route('/update', methods=['GET'])
def update():
    return utils.git_pull()

@app.route('/download/<location>/<audio>', methods=['GET'])
def download(location, audio):
    if location == 'pi':
        return send_file(os.path.join(utils.audio_folder, audio), as_attachment=False)
    else:
        return utils.download_from_server(audio)
    
@app.route('/upload-to-server', methods=['GET'])
def upload_to_server():
    global upload_object
    if upload_object is not None:
        return ''
    else:
        upload_object = utils.sync()
        message = upload_object.upload_to_server()
        upload_object = None
        return message

@app.route('/upload-message', methods=['GET'])
def upload_message():
    if upload_object is None:
        return ''
    else:
        return upload_object.message()

@app.route('/get-step', methods=['GET'])
def get_step():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
    # app.run(host='127.0.0.1', debug=True, port=8000)
    
    