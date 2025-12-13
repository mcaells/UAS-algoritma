import sqlite3

DATABASE = 'scheduler.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 1. Tabel Users (BARU: Untuk Login & Register)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')

    # 2. Tabel Schedules (Jadwal)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            notes TEXT
        );
    ''')

    # 3. Tabel Tasks (Tugas)
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
            
    conn.commit()
    conn.close()
    print("Database 'scheduler.db' berhasil diinisialisasi dengan tabel: users, schedules, tasks.")

if __name__ == '__main__':
    init_db()