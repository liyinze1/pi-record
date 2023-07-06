from flask import Flask, render_template, send_file
import utils
import os
app = Flask(__name__)

vpn_thread = utils.vpn()
record_thread = utils.record()

save_location = utils.save_location
car_table = utils.car_table('car_table.csv')

upload_object = None

utils.role = 'pi'

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/save-location/<new_save_location>', methods=['GET'])
def set_save_location(new_save_location):
    global save_location
    assert save_location in ('both', 'pi', 'server')
    save_location = new_save_location
    return 'save locations has been updated to ' + save_location

@app.route('/record/<vin>', methods=['GET'])
def record(vin):
    return str(record_thread.record(vin, save_location))

@app.route('/test-loss-rate', methods=['GET'])
def test_loss_rate():
    record_thread.record('test', 'test')
    return record_thread.stop_test()

@app.route('/stop', methods=['GET'])
def stop():
    return str(record_thread.stop())

@app.route('/check-vpn', methods=['GET'])
def check_vpn():
    app.logger.info("checking vpn")
    return str(vpn_thread.check())

@app.route('/connect-vpn', methods=['GET'])
def connect_vpn():
    return str(vpn_thread.connect())

@app.route('/shut-down', methods=['POST'])
def shut_down():
    return vpn_thread.shut_down()

@app.route('/reboot', methods=['POST'])
def reboot():
    return vpn_thread.reboot()

@app.route('/report/<vin>/<status>', methods=['GET'])
def report(vin, status):
    vin_file = record_thread.record_filename
    if vin_file == None:
        return "no recording"
    if vin not in vin_file:
        return "no recording for new vin"
    record_thread.step = 'scan'
    if save_location in ('pi', 'both'):
        car_table.update(vin_file, status)
    if save_location in ('server', 'both'):
        return utils.report_to_server(vin, status)
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
    return record_thread.step

if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True, port=443, ssl_context='adhoc')
    app.run(host='0.0.0.0', debug=True, port=443, ssl_context=('cert.pem', 'key.pem'))
    