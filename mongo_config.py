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
    _client = None
    _db = None
    
    @staticmethod
    def get_database():
        """Get MongoDB database connection with lazy initialization"""
        if MongoConfig._db is None:
            try:
                uri = MongoConfig.MONGO_URI
                
                # Handle URL encoding for special characters in password
                if 'mongodb+srv://' in uri and '@' in uri:
                    try:
                        parts = uri.split('://', 1)[1]
                        if '@' in parts:
                            creds, rest = parts.split('@', 1)
                            if ':' in creds:
                                user, password = creds.split(':', 1)
                                encoded_password = quote_plus(password)
                                uri = f"mongodb+srv://{user}:{encoded_password}@{rest}"
                    except:
                        pass
                
                # Optimized connection settings for Render
                MongoConfig._client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000,
                    maxPoolSize=10,
                    retryWrites=True
                )
                
                # Test connection
                MongoConfig._client.admin.command('ping')
                MongoConfig._db = MongoConfig._client[MongoConfig.DATABASE_NAME]
                print("MongoDB connected successfully")
                
            except Exception as e:
                print(f"MongoDB connection failed: {e}")
                # Return None to handle gracefully in application
                return None
                
        return MongoConfig._db

# Lazy database instance
def get_db():
    return MongoConfig.get_database()

db = None  # Will be initialized on first use

# Collection names
COLLECTIONS = {
    'users': 'users',
    'themes': 'themes', 
    'initiatives': 'initiatives',
    'dialogues': 'dialogues',
    'contact_shares': 'contact_shares'
}