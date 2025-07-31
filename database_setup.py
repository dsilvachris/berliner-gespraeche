#!/usr/bin/env python3
"""
Database setup script for Berliner Gespräche
Run this script to create the SQLite database and tables
"""

from app import app, db

def create_database():
    """Create the SQLite database and tables"""
    with app.app_context():
        db.create_all()
        print("SQLite database 'berliner_gespraeche.db' created successfully!")
        print("All tables created")

if __name__ == "__main__":
    create_database()
    print("Database setup complete!")
    print("Database file: berliner_gespraeche.db")