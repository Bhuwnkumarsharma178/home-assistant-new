from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('FRIDAY_SECRET_KEY', 'friday_secret')

# In-memory user store: {email: {username, password}}
USERS = {
    'admin@friday.com': {'username': 'admin', 'password': 'friday123'}
}

# Simulated IoT endpoints (replace with your actual endpoints)
DEVICE_STATUS = {
    'light': 'off',
    'fan': 'off',
    'door': 'closed',
    'thermostat': '22°C',
    'curtain': 'closed',
    'bathroom': 'off',
}

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        if not email or not username or not password:
            error = 'All fields are required.'
        elif email in USERS:
            error = 'Email already registered.'
        else:
            USERS[email] = {'username': username, 'password': password}
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = USERS.get(email)
        if user and user['password'] == password:
            session['logged_in'] = True
            session['user_email'] = email
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid email or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html', status=DEVICE_STATUS, username=session.get('username'))

@app.route('/api/status', methods=['GET'])
def get_status():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(DEVICE_STATUS)

@app.route('/api/control', methods=['POST'])
def control_device():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json(force=True)
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    device = data.get('device')
    action = data.get('action')
    if device not in DEVICE_STATUS:
        return jsonify({'error': 'Unknown device'}), 400

    # Only change status for valid actions
    if device == 'thermostat':
        DEVICE_STATUS[device] = action
    elif device in ['door', 'curtain']:
        if action == 'open':
            DEVICE_STATUS[device] = 'open'
        elif action == 'close':
            DEVICE_STATUS[device] = 'closed'
    elif device == 'bathroom':
        if action == 'on':
            DEVICE_STATUS[device] = 'on'
        elif action == 'off':
            DEVICE_STATUS[device] = 'off'
    elif device == 'light':
        if action == 'on':
            DEVICE_STATUS[device] = 'on'
        elif action == 'off':
            DEVICE_STATUS[device] = 'off'
    # else: ignore unrecognized actions

    return jsonify({'status': DEVICE_STATUS[device]})

if __name__ == '__main__':
    app.run(debug=True) 