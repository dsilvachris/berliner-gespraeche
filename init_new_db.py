#!/usr/bin/env python3
"""
Initialize New Database Schema
Creates tables and populates with reference data
"""

from app import app
from models import *
from migrate_database import populate_themes, populate_initiatives, create_default_user

def init_database():
    """Initialize new database with schema and reference data"""
    print("Initializing new database schema...")
    
    with app.app_context():
        # Drop all tables and recreate (fresh start)
        db.drop_all()
        db.create_all()
        print("Database tables created")
        
        # Populate reference data
        populate_themes()
        populate_initiatives()
        create_default_user()
        
        print("Database initialization completed!")
        print("You can now run the migration script to transfer old data")

if __name__ == '__main__':
    init_database()