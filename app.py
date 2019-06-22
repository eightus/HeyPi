from flask import Flask, render_template, session, redirect, url_for, request, jsonify, make_response
from config.db_access import Database
from functools import wraps
from speech.recorder import Record
from speech.action import Action
from gpiozero import LED, Button
from subprocess import Popen
import os
from datetime import datetime


_DATABASE_NAME = 'assignment'
_LED = None
_BUTTON = None
_SPEECH = None
_DHT11_PIN = None
_BRIGHTNESS = None

app = Flask(__name__)
app.config.update(
    DEBUG=False,
    SECRET_KEY="Secret!"
)

conn = None
record = None
action = None


# Initialisation
def initialise():
    global _LED, _BUTTON, _DATABASE_NAME, _DHT11_PIN, _SPEECH, record, conn, action

    dir_path = os.path.dirname(os.path.realpath(__file__))
    cmd_dht11 = 'sudo python3 {}/equipment/dht11.py'.format(dir_path)
    cmd_ldr = 'sudo python3 {}/equipment/ldr.py'.format(dir_path)
    Popen(cmd_dht11, shell=True)
    Popen(cmd_ldr, shell=True)

    _DATABASE_NAME = 'assignment'
    conn = Database(_DATABASE_NAME)

    data = conn.get_configuration()
    _LED = LED(int(data['LED']))

    speed, pitch = data['speech_speed'], data['speech_pitch']
    gender = 'en+m3' if data['speech_gender'] == 'male' else 'en+f3'
    _SPEECH = 'espeak -s{} -v{} -p{} -k5 -z '.format(speed, gender, pitch)

    action = Action(conn, _SPEECH, _LED)
    record = Record(conn, action)

    _BUTTON = Button(int(data['button']), pull_up=False)
    _BUTTON.when_pressed = record.start_record
    _BUTTON.when_released = record.stop_record


def re_initialise():
    global conn, action, _LED, _SPEECH, _BUTTON

    data = conn.get_configuration()
    speed, pitch = data['speech_speed'], data['speech_pitch']
    gender = 'en+m3' if data['speech_gender'] == 'male' else 'en+f3'
    _SPEECH = 'espeak -s{} -v{} -p{} -k5 -z '.format(speed, gender, pitch)
    try:
        _LED = LED(int(data['LED']))
    except:
        pass
    action.reload_speech(_SPEECH)
    action.reload_led(_LED)


#  Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = request.form
        username = form['username']
        password = form['password']

        check_credential = conn.login(username, password)

        if check_credential:
            session['username'] = username
            session['login_status'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", status='fail')

    return render_template("login.html")


#  Dashboard Page
@app.route('/')
def dashboard():
    if not load('refresh'):
        return redirect(url_for("login"))
    return render_template('index.html')


#  Statistics
@app.route('/statistics')
def statistics():
    if not load():
        return redirect(url_for("login"))

    return render_template('statistic.html')

#  Log Page
@app.route('/log')
def log():
    if not load():
        return redirect(url_for("login"))

    get_log = conn.get_log()
    return render_template('log.html', full_log=get_log)


#  Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if not load():
        return redirect(url_for("login"))

    if request.method == 'POST':
        form = request.form
        username = form['username']
        password = form['password']

        if conn.register(username, password):
            return render_template("register.html", status='success', new_user=username)
        else:
            return render_template("register.html", status='fail', new_user=username)
    else:
        return render_template("register.html")

#  Settings Page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not load():
        return redirect(url_for("login"))

    condition = conn.get_condition_clean()
    config = conn.get_configuration()

    if request.method == 'POST' and 'speech' in request.form:
        form = request.form.to_dict()
        text, match_type, action_func, speech = form['speech'].lower(), form['type'], form['action'], form['speech_out']

        if action_func == 'speak':
            action_func = "speak='" + speech + "'"

        if conn.insert_chat_condition(text, match_type, action_func):
            new_condition = conn.get_condition_clean()
            action.load_condition()
            return render_template("setting.html", status='success', condition=new_condition, data='Added condition', config=config)
        else:
            return render_template("setting.html", status='fail', condition=condition, data='Failed to add condition', config=config)

    elif request.method == 'POST' and 'cd' in request.form:
        selected = request.form.getlist('cd')
        conn.delete_chat_condition(selected)
        new_condition = conn.get_condition_clean()
        action.load_condition()
        return render_template("setting.html", status='success', condition=new_condition, data='Deleted condition', config=config)

    elif request.method == 'POST' and 'speech_gender' in request.form:
        form = request.form.to_dict()
        conn.update_configuration(form)
        re_initialise()
        new_config = conn.get_configuration()
        return render_template("setting.html", status='success', condition=condition, data='Updated Settings', config=new_config)
    else:
        return render_template("setting.html", condition=condition, config=config)

#  Logout Page
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


#  Base Loading On Every Page
def load(func='basic'):
    if 'username' not in session:
        return False

    if func == 'basic':
        return True
    elif func == 'refresh':
        #  The only time when refresh is used, is when Login & PUT Request & Refresh Btn is pressed
        session['temperature'] = str(conn.get_temperature()['value']) + '°'
        session['humidity'] = conn.get_humidity()['value']
        session['brightness'] = conn.get_brightness()['value']
        session['time'] = 'Last Updated: ' + str(conn.get_temperature()['time'])
        return True


#  REST API Authentication Decorator
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'username' and auth.password == 'password':
            return f(*args, **kwargs)
        return make_response('Unable to verify login', 401, {'WWW-Authenticate': 'Basic-realm="Login Required"'})

    return decorated


#  GET Request Information
@app.route('/update/<choice>')
def get_update(choice):
    if choice == 'temperature':
        return jsonify(conn.get_temperature())
    elif choice == 'brightness':
        return jsonify(conn.get_brightness())
    elif choice == 'led':
        return jsonify(conn.get_led(_LED))
    elif choice == 'humidity':
        return jsonify(conn.get_humidity())
    elif choice == 'cfg':
        print(conn.get_configuration())
        return jsonify(conn.get_configuration())
    else:
        return 'Error 404'


@app.route('/api/get_all', methods=['GET', 'POST'])
def get_graph_data():
    if request.method == 'POST':
        return jsonify(conn.get_all_stat())
    else:
        return jsonify('Error'), 400


@app.route('/api/get_chat', methods=['GET', 'POST'])
def get_chat_data():
    if request.method == 'POST':
        return jsonify(conn.get_log_clean())
    else:
        return jsonify('Error', 400)


if __name__ == '__main__':
    initialise()
    app.run(host='0.0.0.0', port=5000)
