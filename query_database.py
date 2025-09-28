#!/usr/bin/env python3
"""
Simple database query script for Berliner Gespräche
"""

import sqlite3
import json
from datetime import datetime

def connect_db():
    """Connect to the database"""
    return sqlite3.connect('berliner_gespraeche.db')

def show_all_dialogues():
    """Show all dialogues in a readable format"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, timestamp, livable_city, partner_interest, topics, notes, 
               district, initiatives, reflection, num_people, duration, 
               email, phone, consent, data_protection
        FROM dialogue
        ORDER BY timestamp DESC
    """)
    
    dialogues = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(dialogues)} dialogues:\n")
    
    for dialogue in dialogues:
        print(f"=== Dialog ID: {dialogue[0]} ===")
        print(f"Timestamp: {dialogue[1]}")
        print(f"District: {dialogue[6]}")
        print(f"Topics: {json.loads(dialogue[4]) if dialogue[4] else 'None'}")
        print(f"Initiatives: {json.loads(dialogue[7]) if dialogue[7] else 'None'}")
        print(f"Participants: {dialogue[9]}, Duration: {dialogue[10]} min")
        print(f"Notes: {dialogue[5]}")
        print("-" * 50)

def get_statistics():
    """Get basic statistics"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Total dialogues
    cursor.execute("SELECT COUNT(*) FROM dialogue")
    total_dialogues = cursor.fetchone()[0]
    
    # Total participants
    cursor.execute("SELECT SUM(num_people) FROM dialogue")
    total_participants = cursor.fetchone()[0] or 0
    
    # Average duration
    cursor.execute("SELECT AVG(duration) FROM dialogue")
    avg_duration = cursor.fetchone()[0] or 0
    
    # Most common district
    cursor.execute("""
        SELECT district, COUNT(*) as count 
        FROM dialogue 
        WHERE district IS NOT NULL 
        GROUP BY district 
        ORDER BY count DESC 
        LIMIT 1
    """)
    top_district = cursor.fetchone()
    
    conn.close()
    
    print("=== STATISTICS ===")
    print(f"Total Dialogues: {total_dialogues}")
    print(f"Total Participants: {total_participants}")
    print(f"Average Duration: {avg_duration:.1f} minutes")
    print(f"Most Common District: {top_district[0] if top_district else 'N/A'}")

if __name__ == "__main__":
    print("=== Berliner Gespräche Database Query ===\n")
    
    try:
        get_statistics()
        print("\n")
        show_all_dialogues()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the database file exists.")