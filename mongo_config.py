"""
MongoDB Configuration for Berliner Gespräche
"""

from pymongo import MongoClient
from datetime import datetime
import os
from urllib.parse import quote_plus

class MongoConfig:
    # MongoDB connection settings
    MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('MONGO_DB_NAME', 'berliner_gespraeche')
    
    @staticmethod
    def get_database():
        """Get MongoDB database connection"""
        uri = MongoConfig.MONGO_URI
        # Handle URL encoding for special characters in password
        if 'mongodb+srv://' in uri and '@' in uri:
            try:
                # Extract and encode credentials if needed
                parts = uri.split('://', 1)[1]
                if '@' in parts:
                    creds, rest = parts.split('@', 1)
                    if ':' in creds:
                        user, password = creds.split(':', 1)
                        # Re-encode the password to handle special characters
                        encoded_password = quote_plus(password)
                        uri = f"mongodb+srv://{user}:{encoded_password}@{rest}"
            except:
                pass  # Use original URI if parsing fails
        
        client = MongoClient(uri)
        return client[MongoConfig.DATABASE_NAME]

# Global database instance
db = MongoConfig.get_database()

# Collection names
COLLECTIONS = {
    'users': 'users',
    'themes': 'themes', 
    'initiatives': 'initiatives',
    'dialogues': 'dialogues',
    'contact_shares': 'contact_shares'
}