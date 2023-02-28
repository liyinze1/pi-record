from flask import Flask, render_template
import utils

app = Flask(__name__)


vpn_thread = utils.vpn()
record_thread = utils.record()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/record/<vin>', methods=['GET'])
def record(vin):
    return str(record_thread.record(vin))

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
    return utils.report(vin,record_thread.record_filename, status)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True, port=443, ssl_context='adhoc')
    app.run(host='0.0.0.0', debug=True, port=443, ssl_context=('cert.pem', 'key.pem'))
    