#!/usr/bin/env python3
from database import db, setup_database
from datetime import datetime, timedelta
import random

def insert_test_data():
    """Insert sample dialogue data for testing"""
    
    # Ensure database is set up
    setup_database()
    
    # Get admin user
    admin_user = db.execute_one("SELECT id FROM users WHERE username = %s", ('Admin',))
    if not admin_user:
        print("Admin user not found. Creating...")
        admin_user_id = db.execute_one(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id",
            ('Admin', 'Admin123')
        )['id']
    else:
        admin_user_id = admin_user['id']
    
    # Sample data
    districts = ['Mitte', 'Neukölln', 'Kreuzberg', 'Prenzlauer Berg', 'Charlottenburg']
    topics = ['Wohnen/Bauwende', 'Mobilität', 'Klimaanpassung', 'Food', 'Building Transition']
    subtopics = ['Affordability', 'Bicycle', 'Heat', 'Local Production', 'Concrete']
    
    sample_dialogues = [
        {
            'livable_city': 'Mehr Grünflächen und bessere öffentliche Verkehrsmittel',
            'partner_interest': 'Sehr interessiert an nachhaltiger Stadtentwicklung',
            'notes': 'Diskussion über Fahrradwege und Parks',
            'district': 'Mitte',
            'topics': ['Mobilität', 'Klimaanpassung'],
            'subtopics': ['Bicycle', 'Trees'],
            'name': 'Max',
            'surname': 'Mustermann',
            'email': 'max@example.com',
            'phone': '+49 30 12345678',
            'consent': True,
            'reflection': 'Sehr produktives Gespräch über Stadtplanung',
            'num_people': 2,
            'duration': 45,
            'family_status': 'Familie mit Kindern'
        },
        {
            'livable_city': 'Bezahlbare Wohnungen für alle',
            'partner_interest': 'Möchte sich für Wohnungspolitik engagieren',
            'notes': 'Gentrification ist ein großes Problem',
            'district': 'Neukölln',
            'topics': ['Wohnen/Bauwende'],
            'subtopics': ['Affordability', 'Gentrification'],
            'name': 'Anna',
            'surname': 'Schmidt',
            'email': 'anna@example.com',
            'phone': '+49 30 87654321',
            'consent': True,
            'reflection': 'Wichtige Erkenntnisse über Wohnungsnot',
            'num_people': 1,
            'duration': 30,
            'family_status': 'Single'
        },
        {
            'livable_city': 'Saubere Luft und weniger Verkehr',
            'partner_interest': 'Umweltschutz ist sehr wichtig',
            'notes': 'E-Mobilität und ÖPNV Ausbau diskutiert',
            'district': 'Kreuzberg',
            'topics': ['Mobilität', 'Klimaanpassung'],
            'subtopics': ['Electric Car', 'Public Transport (ÖPNV)'],
            'name': '',
            'surname': '',
            'email': '',
            'phone': '',
            'consent': False,
            'reflection': 'Gute Ideen für nachhaltige Mobilität',
            'num_people': 3,
            'duration': 60,
            'family_status': 'WG'
        }
    ]
    
    print("Inserting test dialogues...")
    
    for i, dialogue in enumerate(sample_dialogues):
        # Create dialogue with random timestamp in last 30 days
        created_at = datetime.now() - timedelta(days=random.randint(0, 30))
        
        dialogue_id = db.execute_one("""
            INSERT INTO dialogues (
                user_id, livable_city, partner_interest, notes, district,
                topics, subtopics, initiative_types, selected_initiatives,
                name, surname, email, phone, consent, data_protection,
                reflection, num_people, duration, family_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            admin_user_id,
            dialogue['livable_city'],
            dialogue['partner_interest'],
            dialogue['notes'],
            dialogue['district'],
            dialogue['topics'],
            dialogue['subtopics'],
            [],  # initiative_types
            [],  # selected_initiatives
            dialogue['name'],
            dialogue['surname'],
            dialogue['email'],
            dialogue['phone'],
            dialogue['consent'],
            dialogue['consent'],  # data_protection same as consent
            dialogue['reflection'],
            dialogue['num_people'],
            dialogue['duration'],
            dialogue['family_status'],
            created_at
        ))['id']
        
        print(f"✓ Created dialogue #{dialogue_id} in {dialogue['district']}")
    
    print(f"\n✅ Successfully inserted {len(sample_dialogues)} test dialogues!")
    print("\nTest login credentials:")
    print("Username: Admin")
    print("Password: Admin123")
    print("\nYou can now:")
    print("1. Start the app: python app.py")
    print("2. Visit: http://localhost:5001")
    print("3. Login and view the dashboard")
    print("4. Test the dialogue flow")

if __name__ == '__main__':
    insert_test_data()