from flask import Flask, render_template
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

@app.route('/stop/<vin>', methods=['GET'])
def stop(vin):
    return str(record_thread.stop(vin))

@app.route('/check-vpn', methods=['GET'])
def check_vpn():
    app.logger.info("checking vpn")
    return str(vpn_thread.check())

@app.route('/connect-vpn', methods=['GET'])
def connect_vpn():
    return str(vpn_thread.connect())

@app.route('/shut_down', methods=['GET'])
def shut_down():
    return vpn_thread.shut_down()

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

if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True, port=443, ssl_context='adhoc')
    app.run(host='0.0.0.0', debug=True, port=443, ssl_context=('cert.pem', 'key.pem'))
    