from flask import Flask, render_template, send_file
import utils
app = Flask(__name__)

vpn_thread = utils.vpn()
record_thread = utils.record()

save_location = 'both'
car_table = utils.car_table('car_table.csv')

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
    if save_location in ('pi', 'both'):
        car_table.update(vin_file, status)
    if save_location in ('server', 'both'):
        return utils.report_to_server(vin, status)
    return 'ok'

@app.route('/check-last-audio/<position>', methods=['GET'])
def check_last_audio(position):
    if position == 'pi':
        return utils.check_last_audio().split('/')[-1]
    else:
        return utils.check_last_audio_server().split('/')[-1]

@app.route('/delete-last-audio/<position>/<audio>', methods=['GET'])
def delete_last_audio(position, audio):
    if position == 'pi':
        return utils.delete_last_audio(audio)
    else:
        return utils.delete_last_audio_server(audio)

@app.route('/update', methods=['GET'])
def update():
    return utils.git_pull()

@app.route('/download', methods=['GET'])
def download():
    audio = utils.check_last_audio()
    if audio != 'None':
        return send_file(audio, as_attachment=False)
    else:
        return 'There is no audio available'

if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True, port=443, ssl_context='adhoc')
    app.run(host='0.0.0.0', debug=True, port=443, ssl_context=('cert.pem', 'key.pem'))
    