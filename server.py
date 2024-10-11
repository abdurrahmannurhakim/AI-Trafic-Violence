from flask import Flask, request, jsonify, redirect, url_for, render_template_string, send_from_directory, redirect, url_for
import sqlite3
import os
import webbrowser
import threading
#from ocr_library import process_image

#glob_slash = "/" #linux
glob_slash = "\\" #windows

app = Flask(__name__, static_folder='database/static')

def get_db_connection():
    conn = sqlite3.connect(str('database' + glob_slash +'login.db'))
    conn.row_factory = sqlite3.Row
    return conn

def find_available_port(starting_port):
    import socket
    port = starting_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) != 0:
                return port
            port += 1

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM login WHERE user = ? AND password = ?', (username, password)).fetchone()

    if user:
        # Update the token in the database
        new_token = user['token']  # This could be regenerated if necessary
        conn.execute('UPDATE login SET token = ? WHERE id = ?', (new_token, user['id']))
        conn.commit()
        conn.close()

        response = jsonify({'status': 'success', 'token': new_token})
        response.set_cookie('token', new_token, httponly=True)
        return response
    else:
        conn.close()
        return jsonify({'status': 'fail', 'message': 'Invalid username or password'}), 401

# Menghubungkan ke database data.db
def get_data_db_connection():
    conn = sqlite3.connect(str('database' + glob_slash +'datalog.db'))
    conn.row_factory = sqlite3.Row
    return conn

# Menghubungkan ke database login.db
def get_db_connection():
    conn = sqlite3.connect(str('database' + glob_slash +'login.db'))
    conn.row_factory = sqlite3.Row
    return conn

def speed_limitation(speed, max_speed):
    if speed <= 5:
        return "not detected"
    elif speed >= (max_speed*2):
        return "out of range"
    else:
        return str(speed) + " km/h"

@app.route('/dashboard', methods=['GET'])
def dashboard():
    filter_date = request.args.get('date', '')

    conn_data = get_data_db_connection()
    query = 'SELECT * FROM datalog'
    params = []
    if filter_date:
        query += ' WHERE date LIKE ?'
        params.append(f'%{filter_date}%')
    
    data = conn_data.execute(query, params).fetchall()
    conn_data.close()
    
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Traffic Violence</title>
        <link rel="stylesheet"  href="{{ url_for('static', filename='dashboard.css') }}">
    </head>
    <body>
        <div class="container">
            <div class="sidebar">
                <h2>Menu</h2>
                <ul>
                    <li><a href="/dashboard" class="active">Dashboard</a></li>
                    <li><a href="/change-user">Change User</a></li>
                    <li><a href="#" onclick="logout()">Logout</a></li>
                </ul>
            </div>
            <div class="content">
                <h1>Traffic Violence</h1>
                <div class="filters">
                    <label for="filter-date">Filter by Date:</label>
                    <input type="text" id="filter-date" placeholder="mm/dd/yyyy" onchange="filterByDate(this.value)">
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Date</th>
                            <th>Plat License</th>
                            <th>Violence Category</th>
                            <th>Vehicle Type</th>
                            <th>Open Photo</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in data %}
                        <tr>
                            <td>{{ row['id'] }}</td>
                            <td>{{ row['date'] }}</td>
                            <td>
                                {% if 'Not Detected' in row['plat_license'] %}
                                    Not Detected
                                {% else %}
                                    <img src="{{ url_for('static', filename= row['plat_license']) }}" alt="Plat License" style="width:100px;height:auto;">
                                {% endif %}
                            </td>
                            <td>{{ row['violence_category'] }}</td>
                            <td>{{ row['vehicle'] }}</td>
                            <td><a href="{{ url_for('photo', id=row['id']) }}">Open Photo</a></td>
                            <td><button onclick="deleteRow({{ row['id'] }})">Delete</button></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        <script>
            function filterByDate(date) {
                const url = new URL(window.location.href);
                url.searchParams.set('date', date);
                window.location.href = url.toString();
            }

            function deleteRow(id) {
                if(confirm('Are you sure you want to delete this record?')) {
                    fetch(`/delete/${id}`, { method: 'DELETE' })
                        .then(response => window.location.reload());
                }
            }

            function logout() {
                fetch('/logout', { method: 'POST' })
                    .then(response => {
                        if (response.ok) {
                            window.location.href = '/';
                        }
                    });
            }
        </script>
    </body>
    </html>
    ''', data=data)

@app.route('/photo/<int:id>', methods=['GET'])
def photo(id):
    conn_data = get_data_db_connection()
    query = 'SELECT * FROM datalog WHERE id = ?'
    data = conn_data.execute(query, (id,)).fetchone()
    
    inspeed = float(data['speed'])
    print(inspeed)
    inmaxspeed = float(data['max_speed'])
    speed = speed_limitation(inspeed, inmaxspeed)
    
    conn_data.close()
    location = 'Bandung'
    if data:
        image_path = data['open_photo']
        plat_license_path = data['plat_license']
        print(plat_license_path)
        #text_ocr = process_image("static/"+plat_license_path)
        text_ocr = "plate number"
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Photo Detail</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='dashboard.css') }}">
        </head>
        <body>
            <div class="photo-container">
                <img src="{{ url_for('static', filename=image_path) }}" alt="Open Photo" class="photo-img">
                <div class="photo-details">
                    <p>
                        <strong>License Plate (img):</strong> 
                        {% if 'Not Detected' in plat_license_path %}
                            Not Detected
                        {% else %}
                            <img src="{{ url_for('static', filename=plat_license_path) }}" alt="Plat License" class="license-img">
                        {% endif %}
                    </p> 
                    <p><strong>Date:</strong> {{ data['date'] }}</p>
                    <p><strong>Speed:</strong> {{ speed }}</p>
                    <p><strong>Max Speed:</strong> {{ data['max_speed'] }} km/hour</p>
                    <p><strong>Vehicle:</strong> {{ data['vehicle'] }}</p>
                    <p><strong>Traffic Violence:</strong> {{ data['violence_category'] }}</p>
                    <p><strong>Location:</strong> {{ location }}</p>
                </div>
                <a href="/dashboard" class="btn-back">Back to Dashboard</a>
            </div>
        </body>
        </html>
        ''', data=data, image_path=image_path, plat_license_path=plat_license_path, location = location, speed = speed, text_ocr=text_ocr)
    else:
        return redirect('/dashboard')


@app.route('/change-user', methods=['GET', 'POST'])
def change_user():
    message = ''
    if request.method == 'POST':
        last_username = request.form['last_username']
        last_password = request.form['last_password']
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM login WHERE user = ? AND password = ?', 
                            (last_username, last_password)).fetchone()
        
        if user:
            conn.execute('UPDATE login SET user = ?, password = ? WHERE id = ?', 
                         (new_username, new_password, user['id']))
            conn.commit()
            message = 'Username and password updated successfully!'
        else:
            message = 'Invalid username or password.'
        
        conn.close()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Change User</title>
        <link rel="stylesheet"  href="{{ url_for('static', filename='dashboard.css') }}">
    </head>
    <body>
        <div class="container">
            <div class="sidebar">
                <h2>Menu</h2>
                <ul>
                    <li><a href="/dashboard">Dashboard</a></li>
                    <li><a href="/change-user" class="active">Change User</a></li>
                    <li><a href="#" onclick="logout()">Logout</a></li>
                </ul>
            </div>
            <div class="content">
                <h1>Change User</h1>
                <form method="POST">
                    <label for="last_username">Last Username</label>
                    <input type="text" id="last_username" name="last_username" required>
                    <label for="last_password">Last Password</label>
                    <input type="password" id="last_password" name="last_password" required>
                    <label for="new_username">New Username</label>
                    <input type="text" id="new_username" name="new_username" required>
                    <label for="new_password">New Password</label>
                    <input type="password" id="new_password" name="new_password" required>
                    <button type="submit">Change User</button>
                    <p>{{ message }}</p>
                </form>
            </div>
        </div>
        <script>
            function logout() {
                fetch('/logout', { method: 'POST' })
                    .then(response => {
                        if (response.ok) {
                            window.location.href = '/';
                        }
                    });
            }
        </script>
    </body>
    </html>
    ''', message=message)

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    conn_data = get_data_db_connection()
    query = 'SELECT open_photo, plat_license FROM datalog WHERE id = ?'
    data = conn_data.execute(query, (id,)).fetchone()
    
    if data:
        # Hapus data dari database
        conn_data.execute('DELETE FROM datalog WHERE id = ?', (id,))
        conn_data.commit()
        conn_data.close()
        
        # Hapus file gambar
        file_path_1 = os.path.join(str('database' + glob_slash + 'static'), data['open_photo'])
        file_path_2 = os.path.join(str('database' + glob_slash +'static'), data['plat_license'])
        try:
            if (file_path_1):
                os.remove(file_path_1)

            if (file_path_2):
                os.remove(file_path_2)
        except FileNotFoundError:
            pass
        
        return '', 204
    else:
        conn_data.close()
        return '', 404

@app.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'status': 'logged out'})
    response.set_cookie('token', '', expires=0)
    return response

@app.route('/')
def login_page():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Page</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    </head>
    <body>
        <div class="login-container">
            <h2>Login</h2>
            <div class="input-group">
                <input type="text" id="username" placeholder="Username">
            </div>
            <div class="input-group">
                <input type="password" id="password" placeholder="Password">
            </div>
            <button onclick="login()">Login</button>
            <p id="notification"></p>
        </div>

        <script>
            async function login() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;

                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                });

                const data = await response.json();
                if (response.ok) {
                    document.cookie = 'token=' + data.token + ';path=/';
                    window.location.href = '/dashboard';
                } else {
                    document.getElementById('notification').textContent = data.message;
                }
            }
        </script>
    </body>
    </html>
    ''')

def open_browser(port):
    webbrowser.open(f'http://127.0.0.1:{port}', new=2)

if __name__ == '__main__':
    port = find_available_port(5000)
    show_port = 0
    if port>5000:
        show_port = port-1
    else:
        show_port = port
    
    # Mulai server Flask dalam thread utama
    threading.Timer(1, open_browser, args=(show_port,)).start()  # Menunggu sejenak sebelum membuka browser
    app.run(debug=True, port=port)