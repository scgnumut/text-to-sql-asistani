import sqlite3
import os
from datetime import datetime
from config.settings import DB_SOHBET


def init_db():
    conn = sqlite3.connect(DB_SOHBET)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
        """
    )
    conn.commit()
    conn.close()


def get_connection():
    conn = sqlite3.connect(DB_SOHBET)
    conn.row_factory = sqlite3.Row
    return conn


def create_session(title=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (title, updated_at) VALUES (?, ?)",
        (title, datetime.now()),
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_sessions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, created_at, updated_at FROM sessions ORDER BY updated_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?",
        (session_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_session_title(session_id, title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
        (title, datetime.now(), session_id),
    )
    conn.commit()
    conn.close()


def delete_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


def get_messages(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, session_id, role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_message(session_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.now()),
    )
    cursor.execute(
        "UPDATE sessions SET updated_at = ? WHERE id = ?",
        (datetime.now(), session_id),
    )
    conn.commit()
    conn.close()
