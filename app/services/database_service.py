import sqlite3
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice
from app.config.settings import Settings
from app.models.event_model import SecurityEvent

class DatabaseService:
    def __init__(self):
        self.conn = sqlite3.connect(Settings.DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_str TEXT, hora_str TEXT, tag TEXT,
                cor TEXT, mensagem TEXT, imagem BLOB
            )
        """)
        self.conn.commit()

    def save_event(self, event: SecurityEvent) -> SecurityEvent:
        img_blob = None
        if event.image:
            ba = QByteArray()
            buff = QBuffer(ba)
            buff.open(QIODevice.WriteOnly)
            event.image.save(buff, "JPEG")
            img_blob = ba.data()
            
        self.cursor.execute("""
            INSERT INTO eventos (data_str, hora_str, tag, cor, mensagem, imagem)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event.date, event.time, event.tag, event.color, event.msg, img_blob))
        self.conn.commit()
        
        event.id = self.cursor.lastrowid
        event.has_image_db = bool(img_blob)
        return event

    def get_recent_events(self, limit=1000) -> list[SecurityEvent]:
        self.cursor.execute("""
            SELECT id, data_str, hora_str, tag, cor, mensagem, 
            CASE WHEN imagem IS NOT NULL THEN 1 ELSE 0 END 
            FROM eventos ORDER BY id ASC LIMIT ?
        """, (limit,))
        
        return [SecurityEvent(
            id=row[0], date=row[1], time=row[2], tag=row[3], 
            color=row[4], msg=row[5], has_image_db=bool(row[6])
        ) for row in self.cursor.fetchall()]