"""
MongoDB Models for Berliner Gespräche
Document-based data structures replacing SQLAlchemy models
"""

from datetime import datetime
from bson import ObjectId
from mongo_config import db, COLLECTIONS

class BaseModel:
    """Base model with common MongoDB operations"""
    
    @classmethod
    def get_collection(cls):
        return db[cls.collection_name]
    
    @classmethod
    def find_one(cls, filter_dict):
        return cls.get_collection().find_one(filter_dict)
    
    @classmethod
    def find(cls, filter_dict=None):
        return list(cls.get_collection().find(filter_dict or {}))
    
    @classmethod
    def insert_one(cls, document):
        document['created_at'] = datetime.utcnow()
        result = cls.get_collection().insert_one(document)
        return result.inserted_id
    
    @classmethod
    def update_one(cls, filter_dict, update_dict):
        update_dict['updated_at'] = datetime.utcnow()
        return cls.get_collection().update_one(filter_dict, {'$set': update_dict})
    
    @classmethod
    def delete_one(cls, filter_dict):
        return cls.get_collection().delete_one(filter_dict)

class User(BaseModel):
    collection_name = COLLECTIONS['users']
    
    @classmethod
    def create_admin(cls):
        """Create admin user if not exists"""
        admin = cls.find_one({'username': 'admin'})
        if not admin:
            admin_id = cls.insert_one({
                'username': 'admin',
                'role': 'admin'
            })
            return admin_id
        return admin['_id']

class Theme(BaseModel):
    collection_name = COLLECTIONS['themes']
    
    @classmethod
    def get_all(cls):
        return cls.find()
    
    @classmethod
    def seed_themes(cls):
        """Seed initial themes"""
        themes = [
            {'_id': 'urban_garden', 'name': 'Urban Garden', 'description': 'Community gardening initiatives'},
            {'_id': 'repair_cafe', 'name': 'Repair Café', 'description': 'Community repair services'},
            {'_id': 'climate_education', 'name': 'Climate Education', 'description': 'Environmental education programs'},
            {'_id': 'policy_advocacy', 'name': 'Policy Advocacy', 'description': 'Climate policy advocacy'},
            {'_id': 'mutual_aid', 'name': 'Mutual Aid', 'description': 'Community support networks'},
            {'_id': 'digital_inclusion', 'name': 'Digital Inclusion', 'description': 'Digital literacy programs'}
        ]
        
        for theme in themes:
            existing = cls.find_one({'_id': theme['_id']})
            if not existing:
                theme['created_at'] = datetime.utcnow()
                cls.get_collection().insert_one(theme)

class Initiative(BaseModel):
    collection_name = COLLECTIONS['initiatives']

class Dialogue(BaseModel):
    collection_name = COLLECTIONS['dialogues']
    
    @classmethod
    def create_dialogue(cls, dialogue_data):
        """Create new dialogue document"""
        dialogue_doc = {
            'user_id': dialogue_data.get('user_id'),
            'livable_city': dialogue_data.get('livable_city', ''),
            'partner_interest': dialogue_data.get('partner_interest', ''),
            'notes': dialogue_data.get('notes', ''),
            'observer_reflection': dialogue_data.get('observer_reflection', ''),
            'num_people': int(dialogue_data.get('num_people', 1)),
            'duration': int(dialogue_data.get('duration', 0)),
            'location': dialogue_data.get('location', ''),
            'is_anonymous': dialogue_data.get('is_anonymous', True),
            'consent_share_contact': dialogue_data.get('consent_share_contact', False),
            
            # Embedded documents
            'districts': dialogue_data.get('districts', []),
            'interest_areas': dialogue_data.get('interest_areas', []),
            'topics': dialogue_data.get('topics', []),
            'subtopics': dialogue_data.get('subtopics', []),
            'initiative_types': dialogue_data.get('initiative_types', []),
            'selected_initiatives': dialogue_data.get('selected_initiatives', []),
            
            # Contact info (only if consent given)
            'contact_info': dialogue_data.get('contact_info') if dialogue_data.get('consent_share_contact') else None
        }
        
        return cls.insert_one(dialogue_doc)
    
    @classmethod
    def get_dashboard_stats(cls):
        """Get dashboard statistics using MongoDB aggregation"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_dialogues': {'$sum': 1},
                    'total_partners': {'$sum': '$num_people'},
                    'total_duration': {'$sum': '$duration'}
                }
            }
        ]
        
        stats = list(cls.get_collection().aggregate(pipeline))
        return stats[0] if stats else {'total_dialogues': 0, 'total_partners': 0, 'total_duration': 0}
    
    @classmethod
    def get_district_stats(cls):
        """Get district statistics"""
        pipeline = [
            {'$unwind': '$districts'},
            {'$group': {'_id': '$districts', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        return list(cls.get_collection().aggregate(pipeline))
    
    @classmethod
    def get_theme_stats(cls):
        """Get theme statistics"""
        pipeline = [
            {'$unwind': '$interest_areas'},
            {'$group': {'_id': '$interest_areas', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        return list(cls.get_collection().aggregate(pipeline))

class ContactShare(BaseModel):
    collection_name = COLLECTIONS['contact_shares']
    
    @classmethod
    def create_contact_share(cls, contact_data):
        """Create contact share document for QR codes"""
        return cls.insert_one(contact_data)