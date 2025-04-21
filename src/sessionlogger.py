import sqlite3
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
        self.conn = sqlite3.connect("cronopio.db")
        self.create_table()

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