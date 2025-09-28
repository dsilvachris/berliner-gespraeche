"""
MongoDB Configuration for Berliner Gespräche
"""

from pymongo import MongoClient
from datetime import datetime
import os
from urllib.parse import quote_plus

class MongoConfig:
    # MongoDB connection settings
    MONGO_URI = 'mongodb://localhost:27017/'
    DATABASE_NAME = 'berliner_gespraeche'
    
    @staticmethod
    def get_database():
        """Get MongoDB database connection"""
        client = MongoClient(MongoConfig.MONGO_URI)
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