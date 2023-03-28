from flask import Flask, request

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload():
    global r
    r = request
    return True
    
app.run(host='127.0.0.1', debug=True, port=8000)