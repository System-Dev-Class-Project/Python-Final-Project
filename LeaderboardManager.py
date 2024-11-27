import sqlite3


class LeaderboardManager:
    def __init__(self, db_path='leaderboard.sqlite'):
        self.db_path = db_path
        self.initialize_database()

        # Check if leaderboard is empty and populate if needed
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM leaderboard')
            if cursor.fetchone()[0] == 0:
                self.populate_initial_leaderboard()
    def initialize_database(self):
        """Create leaderboard database and table if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    time REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_score(self, username, difficulty, game_time):
        """Add a new score to the leaderboard."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO leaderboard (username, difficulty, time) 
                VALUES (?, ?, ?)
            ''', (username, difficulty, game_time))
            conn.commit()

    def get_top_scores(self, limit=10):
        """Retrieve top scores sorted by time."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT username, difficulty, time 
                FROM leaderboard 
                ORDER BY time ASC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
    def populate_initial_leaderboard(self):
        """Add some initial sample scores to the leaderboard."""
        sample_scores = [
            ('Alice', 'easy', 120.5),
            ('Bob', 'medium', 180.7),
            ('Charlie', 'hard', 250.3),
            ('David', 'easy', 95.2),
            ('Eve', 'medium', 165.4),
            ('Frank', 'hard', 210.6),
            ('Grace', 'easy', 110.8),
            ('Henry', 'medium', 195.2),
            ('Isabelle', 'hard', 275.9),
            ('Jack', 'easy', 88.6)
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for username, difficulty, game_time in sample_scores:
                cursor.execute('''
                    INSERT INTO leaderboard (username, difficulty, time) 
                    VALUES (?, ?, ?)
                ''', (username, difficulty, game_time))
            conn.commit()