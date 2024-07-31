from flask import Flask
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 22000))

app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=8080, use_reloader=False)
    