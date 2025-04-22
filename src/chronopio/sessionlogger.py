import sqlite3, os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SessionData:
    taskid: int
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
        dbExists = os.path.exists(dbPath)
        self.conn = sqlite3.connect(dbPath)
        if not dbExists:
            self.create_db_objects()

    def __del__(self):
        if self.conn:
            self.conn.close()

    def get_user_data_dir(self):
        return Path(os.getenv('XDG_DATA_HOME', str(Path.home() / '.local' / 'share'))) / 'chronopio'
    

    def create_db_objects(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL, 
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration INTEGER NOT NULL,
                mode TEXT NOT NULL,
                sessiondate INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessiondate ON sessions(sessiondate)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
	            id	INTEGER PRIMARY KEY AUTOINCREMENT,
	            parent	INTEGER NOT NULL DEFAULT 0,
	            title	TEXT NOT NULL,
	            tags	TEXT
            )
        """)
        
        cursor.execute("""
            SELECT count(1) FROM tasks
        """)
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("""
                INSERT INTO tasks (title, tags)
                    VALUES ('Free Task', 'Free')
            """)

        self.conn.commit()


    def save_session(self, session: SessionData):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (task_id, start_time, end_time, duration, mode, sessiondate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session.taskid, 
            session.start_time, 
            session.end_time, 
            session.duration, 
            session.mode, 
            session.sessiondate
        ))
        self.conn.commit()

    
    def get_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, title FROM tasks
        """)

        rows = cursor.fetchall()

        return rows
