#!/usr/bin/env python3
"""
Database viewer for Berliner Gespräche
View and export database contents
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime

def view_database():
    """View all dialogues in the database"""
    conn = sqlite3.connect('berliner_gespraeche.db')
    
    query = """
    SELECT id, timestamp, livable_city, partner_interest, topics, notes, 
           district, initiatives, reflection, num_people, duration, 
           email, phone, consent, data_protection
    FROM dialogue
    ORDER BY timestamp DESC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"Total dialogues: {len(df)}")
    print("\nRecent dialogues:")
    print(df.head())
    
    return df

def export_to_excel(filename=None):
    """Export database to Excel file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"berliner_gespraeche_export_{timestamp}.xlsx"
    
    conn = sqlite3.connect('berliner_gespraeche.db')
    
    # Main dialogue data
    df = pd.read_sql_query("""
        SELECT id, timestamp, livable_city, partner_interest, topics, notes, 
               district, initiatives, reflection, num_people, duration, 
               email, phone, consent, data_protection
        FROM dialogue
        ORDER BY timestamp DESC
    """, conn)
    
    # Parse JSON fields for better readability
    df['topics_parsed'] = df['topics'].apply(lambda x: ', '.join(json.loads(x)) if x else '')
    df['initiatives_parsed'] = df['initiatives'].apply(lambda x: ', '.join(json.loads(x)) if x else '')
    
    # Create summary statistics
    summary_data = {
        'Total Dialogues': [len(df)],
        'Total Participants': [df['num_people'].sum()],
        'Average Duration (min)': [df['duration'].mean()],
        'Most Common District': [df['district'].mode().iloc[0] if not df['district'].mode().empty else 'N/A']
    }
    summary_df = pd.DataFrame(summary_data)
    
    # Export to Excel with multiple sheets
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Dialogues', index=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    conn.close()
    print(f"Data exported to: {filename}")
    return filename

def export_to_csv(filename=None):
    """Export database to CSV file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"berliner_gespraeche_export_{timestamp}.csv"
    
    df = view_database()
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Data exported to: {filename}")
    return filename

if __name__ == "__main__":
    print("=== Berliner Gespräche Database Viewer ===\n")
    
    try:
        # View database contents
        df = view_database()
        
        # Export options
        print("\nExport options:")
        print("1. Excel (.xlsx)")
        print("2. CSV (.csv)")
        print("3. Both")
        
        choice = input("\nChoose export format (1/2/3) or press Enter to skip: ").strip()
        
        if choice == "1":
            export_to_excel()
        elif choice == "2":
            export_to_csv()
        elif choice == "3":
            export_to_excel()
            export_to_csv()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the database file exists and contains data.")