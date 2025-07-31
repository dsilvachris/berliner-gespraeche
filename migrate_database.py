#!/usr/bin/env python3
"""
Database migration script to add new columns
"""

import sqlite3
import os

def migrate_database():
    db_path = 'berliner_gespraeche.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Run the app first to create it.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add new columns
        cursor.execute("ALTER TABLE dialogue ADD COLUMN subtopics TEXT")
        print("Added subtopics column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("subtopics column already exists")
        else:
            print(f"Error adding subtopics: {e}")
    
    try:
        cursor.execute("ALTER TABLE dialogue ADD COLUMN topic_notes TEXT")
        print("Added topic_notes column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("topic_notes column already exists")
        else:
            print(f"Error adding topic_notes: {e}")
    
    conn.commit()
    conn.close()
    print("Database migration complete!")

if __name__ == "__main__":
    migrate_database()