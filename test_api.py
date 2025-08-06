#!/usr/bin/env python3
"""
Test script for API endpoints
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api/v1'

def test_lookup_endpoints():
    """Test all lookup endpoints"""
    print("Testing Lookup Endpoints...")
    
    endpoints = [
        '/lookup/themes',
        '/lookup/initiatives', 
        '/lookup/topics',
        '/lookup/districts'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(BASE_URL + endpoint)
            print(f"GET {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Returned {len(data)} items")
            else:
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"  Connection error: {e}")
        print()

def test_create_initiative():
    """Test creating a new initiative"""
    print("Testing Create Initiative...")
    
    new_initiative = {
        "name": "Test Garden Initiative",
        "description": "A test garden for API testing",
        "districts": ["Mitte", "Kreuzberg"],
        "themes": ["Urban Garden"],
        "link": "test@example.com"
    }
    
    try:
        response = requests.post(
            BASE_URL + '/initiatives',
            json=new_initiative,
            headers={'Content-Type': 'application/json'}
        )
        print(f"POST /initiatives: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Connection error: {e}")
    print()

def test_submit_dialogue():
    """Test submitting a dialogue"""
    print("Testing Submit Dialogue...")
    
    dialogue_data = {
        "mainInterest": "Urban gardening and sustainability",
        "livableCity": "A city with green spaces and community gardens",
        "notes": "Very interested in local food production",
        "topicDetails": {
            "food": {
                "food_systems": {
                    "selectedOptions": ["local_production", "urban_farming"],
                    "customNote": "Participant emphasized local food security"
                }
            }
        },
        "districts": ["Mitte"],
        "interestAreas": ["Urban Garden"],
        "shareContact": False,
        "contactInfo": "",
        "isAnonymous": True,
        "observerReflection": "Great conversation about urban agriculture",
        "surprise": "Participant had extensive knowledge about permaculture",
        "numPeople": 2,
        "duration": 25
    }
    
    try:
        response = requests.post(
            BASE_URL + '/dialogues',
            json=dialogue_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"POST /dialogues: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Connection error: {e}")
    print()

if __name__ == '__main__':
    print("API Testing Script")
    print("Make sure the Flask app is running on localhost:5000")
    print("=" * 50)
    
    test_lookup_endpoints()
    test_create_initiative()
    test_submit_dialogue()
    
    print("Testing completed!")