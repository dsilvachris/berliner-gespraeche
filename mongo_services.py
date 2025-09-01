"""
MongoDB Service Layer for Berliner Gespräche
Handles all database operations with GDPR compliance
"""

import json
from datetime import datetime
from bson import ObjectId
from mongo_models import User, Theme, Initiative, Dialogue, ContactShare

class DialogueService:
    """Service for managing dialogues with GDPR compliance"""
    
    @staticmethod
    def create_dialogue(session_data, user_id=None):
        """Create new dialogue from session data"""
        
        # Get or create admin user
        if not user_id:
            user_id = User.create_admin()
        
        # Determine anonymity and consent
        consent = session_data.get('consent', 'no')
        is_anonymous = consent != 'yes'
        consent_share_contact = consent == 'yes'
        
        # Prepare contact info (only if consent given)
        contact_info = None
        if consent_share_contact:
            contact_info = {
                'name': f"{session_data.get('name', '')} {session_data.get('surname', '')}".strip(),
                'email': session_data.get('email', ''),
                'phone': session_data.get('phone', ''),
                'data_protection': session_data.get('data_protection', ''),
                'family_status': session_data.get('family_status', '')
            }
            # Only store if there's actual contact info
            if not any([contact_info['name'], contact_info['email'], contact_info['phone']]):
                contact_info = None
        
        # Prepare dialogue data
        dialogue_data = {
            'user_id': user_id,
            'livable_city': session_data.get('livable_city', ''),
            'partner_interest': session_data.get('partner_interest', ''),
            'notes': session_data.get('notes', ''),
            'observer_reflection': session_data.get('reflection', ''),
            'num_people': int(session_data.get('num_people', 1)),
            'duration': int(session_data.get('duration', 0)),
            'location': session_data.get('location', ''),
            'is_anonymous': is_anonymous,
            'consent_share_contact': consent_share_contact,
            'contact_info': contact_info,
            
            # Arrays for embedded data
            'districts': [session_data.get('district')] if session_data.get('district') else [],
            'topics': session_data.get('topics', []),
            'subtopics': session_data.get('subtopics', []),
            'initiative_types': session_data.get('initiative_types', []),
            'selected_initiatives': session_data.get('selected_initiatives', []),
            'interest_areas': session_data.get('initiative_types', [])  # Map initiative types to interest areas
        }
        
        return Dialogue.create_dialogue(dialogue_data)
    
    @staticmethod
    def get_dialogue_summary(dialogue_id):
        """Get dialogue summary for PDF generation"""
        try:
            dialogue = Dialogue.find_one({'_id': ObjectId(dialogue_id)})
            if not dialogue:
                return None
            
            return {
                'dialogue': dialogue,
                'districts': dialogue.get('districts', []),
                'interest_areas': dialogue.get('interest_areas', []),
                'topics': dialogue.get('topics', []),
                'subtopics': dialogue.get('subtopics', []),
                'contact_info': dialogue.get('contact_info') if dialogue.get('consent_share_contact') else None
            }
        except:
            return None
    
    @staticmethod
    def get_dashboard_data():
        """Get dashboard statistics"""
        # Get basic stats
        stats = Dialogue.get_dashboard_stats()
        
        # Get all dialogues for detailed view
        dialogues = Dialogue.find()
        
        # Get district stats
        district_stats = Dialogue.get_district_stats()
        districts = {item['_id']: item['count'] for item in district_stats}
        
        # Get theme stats
        theme_stats = Dialogue.get_theme_stats()
        themes = {item['_id']: item['count'] for item in theme_stats}
        
        # Get topic stats
        topics = {}
        for dialogue in dialogues:
            for topic in dialogue.get('topics', []):
                topics[topic] = topics.get(topic, 0) + 1
        
        return {
            'total_dialogues': stats.get('total_dialogues', 0),
            'total_partners': stats.get('total_partners', 0),
            'total_duration': stats.get('total_duration', 0),
            'districts': districts,
            'themes': themes,
            'topics': topics,
            'dialogues': dialogues
        }

class InitiativeService:
    """Service for managing initiatives"""
    
    @staticmethod
    def get_initiatives_by_district_and_theme(district, theme_ids):
        """Get initiatives filtered by district and themes"""
        if not theme_ids:
            return []
        
        # In MongoDB, we can use more flexible queries
        filter_query = {
            'districts': district,
            'themes': {'$in': theme_ids}
        }
        
        return Initiative.find(filter_query)
    
    @staticmethod
    def get_all_themes():
        """Get all available themes"""
        return Theme.get_all()

class UserService:
    """Service for managing users"""
    
    @staticmethod
    def get_or_create_admin():
        """Get or create admin user"""
        admin = User.find_one({'username': 'admin'})
        if not admin:
            admin_id = User.create_admin()
            admin = User.find_one({'_id': admin_id})
        return admin

class ContactShareService:
    """Service for managing contact shares (QR codes)"""
    
    @staticmethod
    def create_contact_share(district, initiatives):
        """Create contact share for QR code"""
        contact_data = {
            'district': district,
            'initiatives': initiatives,
            'timestamp': datetime.utcnow()
        }
        return ContactShare.create_contact_share(contact_data)
    
    @staticmethod
    def get_contact_share(contact_id):
        """Get contact share by ID"""
        try:
            return ContactShare.find_one({'_id': ObjectId(contact_id)})
        except:
            return None