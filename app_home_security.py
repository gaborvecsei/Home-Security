"""
 *****************************************************
 *
 *              Gabor Vecsei
 * Email:       vecseigabor.x@gmail.com
 * Blog:        https://gaborvecsei.wordpress.com/
 * LinkedIn:    www.linkedin.com/in/gaborvecsei
 * Github:      https://github.com/gaborvecsei
 * Twitter:     https://twitter.com/GAwesomeBE
 *
 *****************************************************
"""

import configparser

from flask import Flask, render_template, request

from HomeSecurityModules import Firebase
from HomeSecurityModules import HomeSecurity, STATUS_STOPPED, STATUS_RUNNING
from HomeSecurityModules import MotionDetector

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

api_key = config.get("Firebase", "apiKey")
auth_domain = config.get("Firebase", "authDomain")
database_url = config.get("Firebase", "databaseURL")
storage_bucket = config.get("Firebase", "storageBucket")
messaging_sender_id = config.get("Firebase", "messagingSenderId")

FIREBASE_CONFIG = {
    "apiKey": api_key,
    "authDomain": auth_domain,
    "databaseURL": database_url,
    "storageBucket": storage_bucket,
    "messagingSenderId": messaging_sender_id
}

FPS = 5
firebase = Firebase(FIREBASE_CONFIG)
detector = MotionDetector(min_detection_area=25000, kernel=(31, 31), refresh=True, refresh_time=5)
home_security = HomeSecurity(firebase, detector)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login_form():
    return render_template('login_form.html')


@app.route('/status')
def get_status():
    dict = {STATUS_RUNNING: "Running", STATUS_STOPPED: "Stopped"}
    return dict[home_security.get_status_code()]


@app.route('/home_security', methods=['GET', 'POST'])
def home():
    email_input = request.form['email']
    password_input = request.form['password']
    app_status_code = request.form['app_status']
    min_detection_area = request.form['min_detection_area']

    if min_detection_area:
        home_security.motion_detector.change_min_detection_area(eval(min_detection_area))

    login_successful = home_security.login(email_input, password_input, 1800)
    if not login_successful:
        return "Wrong email or password!"

    if app_status_code == "start":
        print("{0} would like to START Home Security".format(email_input))
        if home_security.get_status_code() == STATUS_STOPPED:
            home_security.start()
            return "Started Home Security"
        else:
            return "Already started"

    if app_status_code == "stop":
        print("{0} would like to STOP Home Security".format(email_input))
        if home_security.get_status_code() == STATUS_RUNNING:
            home_security.stop()
            return "Home Security Stopped"
        else:
            return "Home Security is not running"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
