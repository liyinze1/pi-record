from flask import Flask
import utils

app = Flask(__name__)

receive_threads = {}

port_controller = utils.port_controll()

car_table = utils.car_table('car_table.csv')

@app.route('/')
def main():
    return "server running"

@app.route('/receive/<vin>', methods=['GET'])
def record(vin):
    receive_thread = utils.receive(vin, port_controller)
    receive_threads[vin] = receive_thread
    return str(receive_thread.port)

@app.route('/stop/<vin>', methods=['POST'])
def stop(vin):
    receive_threads[vin].stop()
    return 'stopped'

@app.route('/check-vpn', methods=['GET'])
def checkvpn():
    return "OK"
    
@app.route('/report/<vin>/<status>', methods=['GET'])
def report(vin, status):
    if vin not in receive_threads:
        return 'vin is not found on the server'
    else:
        return car_table.update(receive_threads.pop(vin).audio_filename, status)

if __name__ == '__main__':
    app.run(host='10.94.0.16', debug=True, port=8000)