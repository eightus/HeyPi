from flask import Flask, render_template, session, redirect, url_for, request, jsonify, make_response
from config.db_access import Database
from functools import wraps
from datetime import datetime


_DATABASE_NAME = 'assignment'
conn = Database(_DATABASE_NAME)

app = Flask(__name__)
app.config.update(
    DEBUG=False,
    SECRET_KEY="Secret!"
)

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

    get_log = conn.get_log(session['username'])
    return render_template('log.html', full_log=get_log)


# #  Register Page
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if not load():
#         return redirect(url_for("login"))
#
#     if request.method == 'POST':
#         form = request.form
#         username = form['username']
#         password = form['password']
#         number = form['number']
#
#         if conn.register(username, password, number):
#             return render_template("register.html", status='success', new_user=username)
#         else:
#             return render_template("register.html", status='fail', new_user=username)
#     else:
#         return render_template("register.html")

#  Settings Page
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not load():
        return redirect(url_for("login"))

    condition = conn.get_condition_clean(session['username'])
    config = conn.get_configuration(session['username'])

    if request.method == 'POST' and 'speech' in request.form:
        form = request.form.to_dict()
        text, match_type, action_func, speech = form['speech'].lower(), form['type'], form['action'], form['speech_out']

        if action_func == 'speak':
            action_func = "speak='" + speech + "'"

        if conn.insert_chat_condition(text, match_type, action_func, session['username']):
            new_condition = conn.get_condition_clean(session['username'])
            #  action.load_condition() --> Tell RaspberryPi to run action.load_condition() function
            return render_template("setting.html", status='success', condition=new_condition,
                                   data='Added condition', config=config)
        else:
            return render_template("setting.html", status='fail', condition=condition,
                                   data='Failed to add condition', config=config)

    elif request.method == 'POST' and 'cd' in request.form:
        selected = request.form.getlist('cd')
        conn.delete_chat_condition(selected, session['username'])
        new_condition = conn.get_condition_clean(session['username'])
        #  action.load_condition() --> Tell RaspberryPi to run action.load_condition() function
        return render_template("setting.html", status='success', condition=new_condition,
                               data='Deleted condition', config=config)

    elif request.method == 'POST' and 'speech_gender' in request.form:
        form = request.form.to_dict()
        conn.update_configuration(form, session['username'])
        #  re_initialise() --> Tell RaspberryPi to run re_initialise() function
        new_config = conn.get_configuration(session['username'])
        return render_template("setting.html", status='success', condition=condition,
                               data='Updated Settings', config=new_config)
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
        session['temperature'] = str(conn.get_temperature(session['username'])['value']) + '°'
        session['humidity'] = conn.get_humidity(session['username'])['value']
        session['brightness'] = conn.get_brightness(session['username'])['value']
        session['time'] = 'Last Updated: ' + str(conn.get_temperature(session['username'])['time'])
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
        return jsonify(conn.get_temperature(session['username']))
    elif choice == 'brightness':
        return jsonify(conn.get_brightness(session['username']))
    elif choice == 'led':
        return jsonify(conn.get_led(session['username']))
    elif choice == 'humidity':
        return jsonify(conn.get_humidity(session['username']))
    elif choice == 'all':
        return jsonify(conn.get_update_all(session['username']))
    elif choice == 'cfg':
        return jsonify(conn.get_configuration(session['username']))
    else:
        return 'Error 404'


@app.route('/api/get_all', methods=['GET', 'POST'])
def get_graph_data():
    if request.method == 'POST':
        return jsonify(conn.get_all_stat(session['username']))
    else:
        return jsonify('Error'), 400


@app.route('/api/get_chat', methods=['GET', 'POST'])
def get_chat_data():
    if request.method == 'POST':
        return jsonify(conn.get_log_clean(session['username']))
    else:
        return jsonify('Error', 400)


if __name__ == '__main__':
    #  initialise() --> RaspberryPi is to run initialise() function at start
    app.run(host='0.0.0.0', port=5000)
