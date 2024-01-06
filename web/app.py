
from flask import Flask, request, jsonify, render_template,redirect,url_for
import RPi.GPIO as GPIO
import time
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO,emit


# basic flask app structure
app = Flask(__name__)
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'thisisasecretkey' #change this
#add database and bcrypt config to the app
database_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'creds.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#add socketio
socketio = SocketIO(app,logger=True, engineio_logger=True)

#login manager
login_manager = LoginManager()
login_manager.init_app(app)

#initial server state
server_state = 'Off'

#GPIO stuff
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)


#database structure id username password
class User(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(80),unique=True,nullable=False)
    password = db.Column(db.String(400),nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#function to create database run once
def create_database():
    with app.app_context():
        db.create_all()

#a secret sign up path only be seen by admin
@app.route('/secret_sign_up',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        #check for existing user
        user = User.query.filter_by(username=username).first()
        if user:
            message = "[-]Error This Username Already Exists"
            return render_template('signup.html',auth_error=message)
        
        #create a new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('signup.html',auth_error='[+]New User Created Successfully')
        
    else:
        return render_template('signup.html',)
    
    
#a login page for user
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        #check for authentication
        if not user or not bcrypt.check_password_hash(user.password,password):
            message = "[-]Error Wrong Username or Password!"
            return render_template('login.html',auth_error = message)
        
        login_user(user)

        return redirect(url_for('server'))
    
    else:
        return render_template('login.html')

#root page
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for('login'))

#home page
@app.route('/server', methods=['GET'])
@login_required
def server():
    return render_template('index.html',server_state=server_state)

#darkweb path
@app.route('/darkweb',methods=['GET'])
@login_required
def dark_web():
    return render_template('darkweb.html')

#server status on or off
@app.route("/status",methods=['POST'])
@login_required
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

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@socketio.on('status_update')
def handle_status_update(data):
    global server_state
    status = data['status']
    server_state = status
    emit('status_update', {'status': status}, broadcast=True)

if __name__ == '__main__':
    create_database()
    socketio.run(app,debug=True,host='0.0.0.0',port=5000,allow_unsafe_werkzeug=True)

