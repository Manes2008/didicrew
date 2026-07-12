# core/database.py
import sqlite3
import os
from datetime import datetime

DB_PATH = "video_projects.db"

def init_db():
    """Khởi tạo database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea TEXT,
            created_at TEXT,
            script TEXT,
            visual_prompt TEXT,
            image_path TEXT,
            voice_text TEXT,
            editor_guide TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_project(idea, script="", visual_prompt="", image_path="", voice_text="", editor_guide=""):
    """Lưu 1 project vào database"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO projects (idea, created_at, script, visual_prompt, image_path, voice_text, editor_guide)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (idea, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), script, visual_prompt, image_path, voice_text, editor_guide))
    
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return project_id

def get_all_projects():
    """Lấy danh sách tất cả project"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, idea, created_at FROM projects ORDER BY created_at DESC")
    projects = cursor.fetchall()
    conn.close()
    return projects

def get_project_by_id(project_id):
    """Lấy chi tiết 1 project"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = cursor.fetchone()
    conn.close()
    return project