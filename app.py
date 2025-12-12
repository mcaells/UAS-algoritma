from flask import Flask, render_template, request, jsonify, g
import sqlite3
import datetime

app = Flask(__name__)
DATABASE = 'scheduler.db'

# =================================================================================
# --- 1. KONFIGURASI DATABASE ---
# =================================================================================

def get_db():
    """Mendapatkan koneksi database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Row factory agar kolom bisa diakses pakai nama (seperti dictionary)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Menutup koneksi saat request selesai."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Helper untuk SELECT."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Helper untuk INSERT, UPDATE, DELETE."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    inserted_id = cur.lastrowid
    cur.close()
    return inserted_id

# =================================================================================
# --- 2. ENDPOINT API (BACKEND JSON) ---
# =================================================================================

# --- API JADWAL ---
@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    schedules_raw = query_db("""
        SELECT id, subject, day, time, notes FROM schedules 
        ORDER BY 
            CASE day 
                WHEN "Senin" THEN 1 WHEN "Selasa" THEN 2 WHEN "Rabu" THEN 3 
                WHEN "Kamis" THEN 4 WHEN "Jumat" THEN 5 WHEN "Sabtu" THEN 6 
                ELSE 7 
            END, 
            time
    """)
    schedules = [dict(s) for s in schedules_raw]
    return jsonify(schedules)

@app.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    required_fields = ['subject', 'day', 'time']
    if not all(field in data and data[field].strip() for field in required_fields):
        return jsonify({'error': 'Subject, Day, and Time are required'}), 400

    new_id = execute_db(
        'INSERT INTO schedules (subject, day, time, notes) VALUES (?, ?, ?, ?)',
        (data['subject'], data['day'], data['time'], data.get('notes', ''))
    )
    return jsonify({'message': 'Schedule added', 'id': new_id}), 201

# --- API TUGAS ---
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks_raw = query_db('SELECT id, subject, name, deadline, notes, done FROM tasks ORDER BY done ASC, deadline ASC')
    tasks = [dict(t) for t in tasks_raw]
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    required_fields = ['subject', 'name', 'deadline']
    if not all(field in data and data[field].strip() for field in required_fields):
        return jsonify({'error': 'Subject, Name, and Deadline are required'}), 400

    new_id = execute_db(
        'INSERT INTO tasks (subject, name, deadline, notes, done) VALUES (?, ?, ?, ?, ?)',
        (data['subject'], data['name'], data['deadline'], data.get('notes', ''), data.get('done', 0))
    )
    new_task = query_db('SELECT id, subject, name, deadline, notes, done FROM tasks WHERE id = ?', (new_id,), one=True)
    return jsonify({'message': 'Task added successfully', 'task': dict(new_task)}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    # Toggle status selesai/belum
    if 'done' in data and len(data) == 1:
        done_value = 1 if data['done'] else 0
        execute_db('UPDATE tasks SET done=? WHERE id=?', (done_value, task_id))
        return jsonify({'message': f'Task {task_id} status updated'})

    # Update full
    done_value = 1 if data.get('done') else 0
    execute_db(
        'UPDATE tasks SET subject=?, name=?, deadline=?, notes=?, done=? WHERE id=?',
        (data['subject'], data['name'], data['deadline'], data.get('notes', ''), done_value, task_id)
    )
    return jsonify({'message': f'Task {task_id} updated'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    execute_db('DELETE FROM tasks WHERE id=?', (task_id,))
    return jsonify({'message': f'Task {task_id} deleted'})

# --- API OVERVIEW (DASHBOARD) ---
@app.route('/api/overview', methods=['GET'])
def get_overview_data():
    pending_tasks_raw = query_db("SELECT name FROM tasks WHERE done = 0 ORDER BY deadline ASC LIMIT 3")
    pending_tasks = [dict(t)['name'] for t in pending_tasks_raw]
    pending_count = query_db("SELECT COUNT(*) as count FROM tasks WHERE done = 0", one=True)['count']

    days = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    # Python weekday(): Senin=0, Minggu=6. Kita geser agar sesuai array days (Minggu=0)
    current_weekday = datetime.date.today().weekday() 
    today_index = (current_weekday + 1) % 7
    today_day = days[today_index]
    
    closest_schedule_raw = query_db(
        "SELECT subject, time FROM schedules WHERE day=? ORDER BY time LIMIT 1",
        (today_day,), one=True)
    
    closest_schedule = dict(closest_schedule_raw) if closest_schedule_raw else None

    return jsonify({
        'pending_count': pending_count,
        'pending_tasks_names': pending_tasks,
        'closest_schedule': closest_schedule,
        'today_day': today_day
    })

# =================================================================================
# --- 3. ENDPOINT VIEW (HTML ROUTING) ---
# =================================================================================

# Dashboard & Halaman Utama
@app.route('/')
@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

# Fitur Utama
@app.route('/jadwal.html')
def jadwal():
    return render_template('jadwal.html')

@app.route('/tugas.html')
def tugas():
    return render_template('tugas.html')

@app.route('/profil.html')
def profil():
    return render_template('profil.html')

# Authentication & Landing Pages (YANG DITAMBAHKAN)
@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/landingpage.html')
def landingpage():
    return render_template('landingpage.html')

@app.route('/forgotpassword.html')
def forgotpassword():
    return render_template('forgotpassword.html')


# =================================================================================
# --- 4. MAIN EXECUTION ---
# =================================================================================

if __name__ == '__main__':
    try:
        from database import init_db
        # Inisialisasi DB saat pertama kali run (pastikan file database.py ada)
        init_db()
    except ImportError:
        print("Pastikan 'database.py' ada dan bisa diimport.")
    
    # Jalankan server
    app.run(debug=True)