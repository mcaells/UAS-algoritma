import sqlite3

def init_db():
    conn = sqlite3.connect('scheduler.db')
    cursor = conn.cursor()

    # Membuat tabel 'schedules'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            notes TEXT
        );
    ''')

    # Membuat tabel 'tasks' (untuk melengkapi updateOverview)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            name TEXT NOT NULL,
            deadline TEXT,
            notes TEXT,
            done INTEGER DEFAULT 0
        );
    ''')

    # Sisipkan data contoh (opsional)
    cursor.execute("SELECT COUNT(*) FROM schedules")
    if cursor.fetchone()[0] == 0:
        schedules_data = [
            ("Pemrograman Web", "Senin", "08:00", "Lab A, Ruang 101"),
            ("Basis Data", "Selasa", "10:30", "Online Meeting"),
            ("Algoritma", "Kamis", "13:00", "Gedung B, Lantai 2"),
        ]
        cursor.executemany(
            'INSERT INTO schedules (subject, day, time, notes) VALUES (?, ?, ?, ?)', 
            schedules_data
        )

    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        tasks_data = [
            ("Pemrograman Web", "Tugas Akhir", "2025-12-25", "Project Flask", 0),
            ("Basis Data", "Kuis 1", "2025-12-15", "Bab Normalisasi", 0),
            ("Algoritma", "Presentasi", "2025-12-10", "Topik Sorting", 1),
        ]
        cursor.executemany(
            'INSERT INTO tasks (subject, name, deadline, notes, done) VALUES (?, ?, ?, ?, ?)', 
            tasks_data
        )
            
    conn.commit()
    conn.close()
    print("Database 'scheduler.db' dan tabel telah diinisialisasi.")

if __name__ == '__main__':
    init_db()


DATABASE = 'scheduler.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Membuat tabel schedules (Jika belum ada)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            notes TEXT
        )
    """)
    
    # Membuat tabel tasks (TUGAS BARU)
    # Kolom 'done' diatur sebagai INTEGER (0=False, 1=True)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            name TEXT NOT NULL,
            deadline TEXT NOT NULL,
            notes TEXT,
            done INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database 'scheduler.db' dan tabel 'schedules' & 'tasks' telah diinisialisasi.")

if __name__ == '__main__':
    init_db()