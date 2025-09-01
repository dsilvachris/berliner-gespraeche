#!/usr/bin/env python3
"""
MongoDB setup script for Sag doch mal, Berlin
Run this script to initialize MongoDB collections and seed data
"""

from mongo_config import db
from mongo_models import User, Theme, Initiative
from datetime import datetime

def create_collections():
    """Create MongoDB collections and indexes"""
    
    # Create indexes for better performance
    db.users.create_index("username", unique=True)
    db.dialogues.create_index("created_at")
    db.dialogues.create_index("user_id")
    db.contact_shares.create_index("timestamp")
    
    print("MongoDB collections and indexes created successfully!")

def seed_initial_data():
    """Seed initial data"""
    
    # Create admin user
    User.create_admin()
    print("Admin user created")
    
    # Seed themes
    Theme.seed_themes()
    print("Themes seeded")
    
    print("Initial data seeded successfully!")

def setup_database():
    """Complete database setup"""
    print("Setting up MongoDB database...")
    
    create_collections()
    seed_initial_data()
    
    print("MongoDB setup complete!")
    print(f"Database: {db.name}")
    print("Collections created:")
    for collection_name in db.list_collection_names():
        print(f"  - {collection_name}")

if __name__ == "__main__":
    setup_database()