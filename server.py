from flask import Flask, render_template
import utils

app = Flask(__name__)

receive_threads = {}

car_status = {}

port_controller = utils.port_controll()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/receive/<vin>', methods=['GET'])
def record(vin):
    receive_thread = utils.receive(vin, port_controller)
    receive_threads[vin] = receive_thread
    return receive_thread.port

@app.route('/stop/<vin>', methods=['POST'])
def stop(vin):
    receive_threads[vin].stop()
    receive_threads.remove(vin)
    
@app.route('/report/<vin>/<status>', methods=['POST'])
def report(vin, status):
    car_status[vin] = status

if __name__ == '__main__':
    app.run(host='10.94.0.31', debug=True, port=8000, ssl_context='adhoc')