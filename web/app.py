
from flask import Flask, request, jsonify, render_template
import RPi.GPIO as GPIO
import time
# basic flask app structure
app = Flask(__name__)
app.static_folder = 'static'

#GPIO stuff
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

#home page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

#darkweb path
@app.route('/darkweb',methods=['GET'])
def dark_web():
    return render_template('darkweb.html')

#server status on or off
@app.route("/status",methods=['POST'])
def server_status():
    status:str = request.json.get('status')

    if status == 'On':
     GPIO.output(17, GPIO.HIGH)
     time.sleep(3)
     GPIO.output(18, GPIO.HIGH)
     time.sleep(1)
     GPIO.output(18, GPIO.LOW)
     print(f"Server Status: {status}")

    else:
     GPIO.output(18, GPIO.HIGH)
     time.sleep(1)
     GPIO.output(18, GPIO.LOW)
     time.sleep(55)
     GPIO.output(17, GPIO.LOW)
     print(f"Server Status: {status}")

    return jsonify({'message': 'Status updated successfully'})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
