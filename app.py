from flask import Flask, render_template, request, jsonify, g
import sqlite3
import datetime

app = Flask(__name__)
DATABASE = 'scheduler.db'
app.secret_key = 'kunci_rahasia_sangat_aman'  # PENTING: Diperlukan untuk sesi/keamanan

# =================================================================================
# --- 1. KONFIGURASI DATABASE ---
# =================================================================================

def get_db():
    """Mendapatkan koneksi database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
    try:
        cur = db.execute(query, args)
        db.commit()
        inserted_id = cur.lastrowid
        cur.close()
        return inserted_id
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return None

# =================================================================================
# --- 2. ENDPOINT API AUTH (LOGIN, REGISTER, FORGOT) - BARU! ---
# =================================================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if not username or not email or not phone or not password:
        return jsonify({'error': 'Semua kolom wajib diisi!'}), 400

    # Cek apakah user sudah ada (Username, Email, atau Phone)
    existing = query_db('SELECT id FROM users WHERE username=? OR email=? OR phone=?', 
                        (username, email, phone), one=True)
    if existing:
        return jsonify({'error': 'Username, Email, atau No. HP sudah terdaftar.'}), 409

    # Simpan User Baru
    new_id = execute_db(
        'INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)',
        (username, email, phone, password)
    )

    if new_id:
        return jsonify({'message': 'Registrasi berhasil! Silakan login.'}), 201
    else:
        return jsonify({'error': 'Gagal mendaftar. Terjadi kesalahan server.'}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    login_input = data.get('login_input') # Bisa Username, Email, atau Phone
    password = data.get('password')

    if not login_input or not password:
        return jsonify({'error': 'Input tidak lengkap.'}), 400

    # Cek User di DB (Cocokkan login_input dengan username ATAU email ATAU phone)
    user = query_db('''
        SELECT * FROM users 
        WHERE (username=? OR email=? OR phone=?) AND password=?
    ''', (login_input, login_input, login_input, password), one=True)

    if user:
        return jsonify({
            'message': 'Login berhasil',
            'user': {
                'username': user['username'],
                'email': user['email']
            }
        }), 200
    else:
        return jsonify({'error': 'Username/Email/No. HP atau Password salah.'}), 401

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.json
    contact = data.get('contact') # Email atau Phone

    if not contact:
        return jsonify({'error': 'Masukkan Email atau Nomor Telepon.'}), 400

    # Cek apakah user ada
    user = query_db('SELECT id, email FROM users WHERE email=? OR phone=?', (contact, contact), one=True)

    if user:
        # Di sini harusnya kirim email beneran pakai SMTP. 
        # Karena ini lokal, kita simulasikan sukses saja.
        return jsonify({'message': f'Link reset password telah dikirim ke {contact} (Simulasi).'}), 200
    else:
        # Demi keamanan, biasanya pesan error tetap bilang "Jika akun ada, link dikirim"
        # Tapi untuk debugging kita kasih tau jujur.
        return jsonify({'error': 'Data tidak ditemukan dalam sistem.'}), 404

# =================================================================================
# --- 3. ENDPOINT API JADWAL & TUGAS (EXISTING) ---
# =================================================================================

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    schedules_raw = query_db("SELECT * FROM schedules ORDER BY time")
    schedules = [dict(s) for s in schedules_raw]
    return jsonify(schedules)

@app.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    new_id = execute_db(
        'INSERT INTO schedules (subject, day, time, notes) VALUES (?, ?, ?, ?)',
        (data['subject'], data['day'], data['time'], data.get('notes', ''))
    )
    return jsonify({'message': 'Schedule added', 'id': new_id}), 201

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks_raw = query_db('SELECT * FROM tasks ORDER BY done ASC, deadline ASC')
    tasks = [dict(t) for t in tasks_raw]
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    new_id = execute_db(
        'INSERT INTO tasks (subject, name, deadline, notes, done) VALUES (?, ?, ?, ?, ?)',
        (data['subject'], data['name'], data['deadline'], data.get('notes', ''), 0)
    )
    return jsonify({'message': 'Task added successfully', 'task': {'id': new_id}}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    if 'done' in data and len(data) == 1:
        execute_db('UPDATE tasks SET done=? WHERE id=?', (1 if data['done'] else 0, task_id))
    else:
        execute_db('UPDATE tasks SET subject=?, name=?, deadline=?, notes=?, done=? WHERE id=?',
                   (data['subject'], data['name'], data['deadline'], data.get('notes', ''), 1 if data.get('done') else 0, task_id))
    return jsonify({'message': 'Task updated'})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    execute_db('DELETE FROM tasks WHERE id=?', (task_id,))
    return jsonify({'message': 'Task deleted'})

@app.route('/api/overview', methods=['GET'])
def get_overview_data():
    pending_count = query_db("SELECT COUNT(*) as count FROM tasks WHERE done = 0", one=True)['count']
    days = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    today_day = days[(datetime.date.today().weekday() + 1) % 7]
    
    closest_schedule_raw = query_db("SELECT subject, time FROM schedules WHERE day=? ORDER BY time LIMIT 1", (today_day,), one=True)
    closest_schedule = dict(closest_schedule_raw) if closest_schedule_raw else None

    return jsonify({
        'pending_count': pending_count,
        'closest_schedule': closest_schedule,
        'today_day': today_day
    })

# =================================================================================
# --- 4. ENDPOINT VIEW (HTML ROUTING) ---
# =================================================================================

@app.route('/')
@app.route('/dashboard.html')
def dashboard(): return render_template('dashboard.html')

@app.route('/jadwal.html')
def jadwal(): return render_template('jadwal.html')

@app.route('/tugas.html')
def tugas(): return render_template('tugas.html')

@app.route('/profil.html')
def profil(): return render_template('profil.html')

@app.route('/login.html')
def login(): return render_template('login.html')

@app.route('/register.html')
def register(): return render_template('register.html')

@app.route('/forgotpassword.html')
def forgotpassword(): return render_template('forgotpassword.html')

if __name__ == '__main__':
    app.run(debug=True)