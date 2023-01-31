from flask import Flask, render_template
import utils

app = Flask(__name__)

vpn_thread = utils.vpn()
record_thread = utils.record()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/record', methods=['GET'])
def record():
    return str(record_thread.record())

@app.route('/stop', methods=['GET'])
def stop():
    return str(record_thread.stop())

@app.route('/check-vpn', methods=['GET'])
def check_vpn():
    return str(vpn_thread.check())

@app.route('/connect-vpn', methods=['GET'])
def connect_vpn():
    return str(vpn_thread.connect())

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8000)