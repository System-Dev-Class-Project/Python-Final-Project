import sqlite3


class UserManager:
    def __init__(self, db_path='users.sqlite'):
        self.db_path = db_path
        self.initialize_database()

    def initialize_database(self):
        """Create users database and table if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            # Add a default admin user if no users exist
            cursor.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                               ('admin', 'password'))
            conn.commit()

    def validate_login(self, username, password):
        """Validate user credentials."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                           (username, password))
            return cursor.fetchone() is not None

    def register_user(self, username, password):
        """Register a new user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                               (username, password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Username already exists