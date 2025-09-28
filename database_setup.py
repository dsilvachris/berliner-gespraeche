#!/usr/bin/env python3
"""
Database setup script for Sag doch mal, Berlin
Run this script to initialize MongoDB collections and seed data
"""

from mongo_setup import setup_database

if __name__ == "__main__":
    setup_database()
    print("MongoDB setup complete!")
    print("Database: MongoDB (berliner_gespraeche)")
    print("Make sure MongoDB is running on localhost:27017")