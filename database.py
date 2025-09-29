import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import json

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            # Try different common PostgreSQL configurations
            configs = [
                {
                    'host': 'localhost',
                    'database': 'berliner_gespraeche',
                    'user': os.getenv('USER', 'postgres'),
                    'password': '',
                    'port': '5432'
                },
                {
                    'host': 'localhost',
                    'database': 'berliner_gespraeche',
                    'user': 'postgres',
                    'password': 'postgres',
                    'port': '5432'
                }
            ]
            
            for config in configs:
                try:
                    self.connection = psycopg2.connect(**config)
                    self.connection.autocommit = True
                    print(f"Connected to PostgreSQL as {config['user']}")
                    return
                except Exception as e:
                    continue
            
            raise Exception("Could not connect with any configuration")
            
        except Exception as e:
            print(f"Database connection error: {e}")
            print("Please ensure PostgreSQL is running and create database manually:")
            print("1. Start PostgreSQL service")
            print("2. Run: createdb berliner_gespraeche")
    
    def execute(self, query, params=None):
        if not self.connection:
            return None
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall()
                return cursor.rowcount
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    def execute_one(self, query, params=None):
        if not self.connection:
            return None
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchone()
                return cursor.rowcount
        except Exception as e:
            print(f"Database error: {e}")
            return None

db = Database()

def setup_database():
    """Initialize database tables"""
    if not db.connection:
        print("No database connection available")
        return
    
    # Create database if it doesn't exist
    try:
        db.execute("CREATE DATABASE berliner_gespraeche")
    except:
        pass  # Database might already exist
    
    # Users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Dialogues table
    db.execute("""
        CREATE TABLE IF NOT EXISTS dialogues (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            livable_city TEXT,
            partner_interest TEXT,
            notes TEXT,
            district VARCHAR(100),
            topics TEXT[],
            subtopics TEXT[],
            initiative_types TEXT[],
            selected_initiatives TEXT[],
            name VARCHAR(100),
            surname VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(50),
            consent BOOLEAN DEFAULT FALSE,
            data_protection BOOLEAN DEFAULT FALSE,
            reflection TEXT,
            num_people INTEGER DEFAULT 1,
            duration INTEGER DEFAULT 0,
            family_status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Contact shares table for QR codes
    db.execute("""
        CREATE TABLE IF NOT EXISTS contact_shares (
            id SERIAL PRIMARY KEY,
            district VARCHAR(100),
            initiatives TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create admin user
    admin_exists = db.execute_one("SELECT id FROM users WHERE username = %s", ('Admin',))
    if not admin_exists:
        db.execute("INSERT INTO users (username) VALUES (%s)", ('Admin',))
    
    print("Database setup completed successfully!")

if __name__ == '__main__':
    setup_database()