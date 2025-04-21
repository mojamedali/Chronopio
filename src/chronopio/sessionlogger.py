import sqlite3, os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SessionData:
    start_time: str 
    end_time: str 
    duration: int 
    mode: str
    sessiondate: int


class SessionLogger():
    def __init__(self):
        userDir = self.get_user_data_dir()
        userDir.mkdir(parents=True, exist_ok=True) 
        dbPath = userDir / 'cronopio.db'
        self.conn = sqlite3.connect(dbPath)
        self.create_table()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def get_user_data_dir(self):
        return Path(os.getenv('XDG_DATA_HOME', str(Path.home() / '.local' / 'share'))) / 'chronopio'
    

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                duration INTEGER,
                mode TEXT,
                sessiondate INTEGER
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessiondate ON sessions(sessiondate)
        """)

        self.conn.commit()


    def save_session(self, session: SessionData):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (start_time, end_time, duration, mode, sessiondate)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session.start_time, 
            session.end_time, 
            session.duration, 
            session.mode, 
            session.sessiondate
        ))
        self.conn.commit()