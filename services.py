"""
Data Service Layer for New Database Schema
Handles all database operations with GDPR compliance
"""

import json
from datetime import datetime
from models import *

class DialogueService:
    """Service for managing dialogues with GDPR compliance"""
    
    @staticmethod
    def create_dialogue(session_data, user_id=1):
        """Create new dialogue from session data"""
        
        # Debug: Print all session data
        print(f"Full session data: {dict(session_data)}")
        
        # Determine anonymity and consent
        consent = session_data.get('consent', 'no')
        is_anonymous = consent != 'yes'
        consent_share_contact = consent == 'yes'
        
        # Create main dialogue record
        dialogue = Dialogue(
            user_id=user_id,
            livable_city=session_data.get('livable_city', ''),
            partner_interest=session_data.get('partner_interest', ''),
            notes=session_data.get('notes', ''),
            observer_reflection=session_data.get('reflection', ''),
            num_people=int(session_data.get('num_people', 1)),
            duration=int(session_data.get('duration', 0)),
            location=session_data.get('location', ''),
            is_anonymous=is_anonymous,
            consent_share_contact=consent_share_contact
        )
        
        db.session.add(dialogue)
        db.session.flush()  # Get the ID
        
        # Add district
        district = session_data.get('district')
        if district:
            district_link = DialogueDistrict(
                dialogue_id=dialogue.id,
                district_name=district
            )
            db.session.add(district_link)
        
        # Add interest areas
        initiative_types = session_data.get('initiative_types', [])
        theme_mappings = {
            'Urban Garden': 'urban_garden',
            'Repair Café': 'repair_cafe',
            'Climate Education': 'climate_education', 
            'Policy Advocacy': 'policy_advocacy',
            'Mutual Aid': 'mutual_aid',
            'Digital Inclusion': 'digital_inclusion'
        }
        
        for init_type in initiative_types:
            theme_id = theme_mappings.get(init_type)
            if theme_id:
                interest_link = DialogueInterestArea(
                    dialogue_id=dialogue.id,
                    interest_area_id=theme_id
                )
                db.session.add(interest_link)
        
        # Add topic selections
        topics = session_data.get('topics', [])
        subtopics = session_data.get('subtopics', [])
        
        # Debug: Print what we're getting from session
        print(f"Session topics: {topics}")
        print(f"Session subtopics: {subtopics}")
        
        for topic in topics:
            topic_selection = DialogueTopicSelection(
                dialogue_id=dialogue.id,
                main_topic_id=topic.lower().replace('/', '_').replace(' ', '_'),
                sub_group_id='main',
                selected_option_id=topic.lower().replace('/', '_').replace(' ', '_')
            )
            db.session.add(topic_selection)
        
        for subtopic in subtopics:
            subtopic_selection = DialogueTopicSelection(
                dialogue_id=dialogue.id,
                main_topic_id='subtopic',
                sub_group_id='detail', 
                selected_option_id=subtopic.lower().replace(' ', '_')
            )
            db.session.add(subtopic_selection)
        
        # Handle PII (only if consent given)
        if consent_share_contact:
            contact_info = {
                'name': f"{session_data.get('name', '')} {session_data.get('surname', '')}".strip(),
                'email': session_data.get('email', ''),
                'phone': session_data.get('phone', ''),
                'data_protection': session_data.get('data_protection', ''),
                'family_status': session_data.get('family_status', '')
            }
            
            # Only store if there's actual contact info
            if any([contact_info['name'], contact_info['email'], contact_info['phone']]):
                participant_contact = ParticipantContact(
                    dialogue_id=dialogue.id,
                    contact_info=json.dumps(contact_info)
                )
                db.session.add(participant_contact)
        
        db.session.commit()
        return dialogue.id
    
    @staticmethod
    def get_dialogue_summary(dialogue_id):
        """Get dialogue summary for PDF generation"""
        dialogue = Dialogue.query.get(dialogue_id)
        if not dialogue:
            return None
        
        # Get districts
        districts = [d.district_name for d in DialogueDistrict.query.filter_by(dialogue_id=dialogue_id)]
        
        # Get interest areas
        interest_areas = []
        for ia in DialogueInterestArea.query.filter_by(dialogue_id=dialogue_id):
            theme = Theme.query.get(ia.interest_area_id)
            if theme:
                interest_areas.append(theme.name)
        
        # Get topics
        topics = []
        subtopics = []
        for ts in DialogueTopicSelection.query.filter_by(dialogue_id=dialogue_id):
            if ts.sub_group_id == 'main':
                topics.append(ts.selected_option_id.replace('_', ' ').title())
            elif ts.sub_group_id == 'detail':
                subtopics.append(ts.selected_option_id.replace('_', ' ').title())
        
        # Get contact info (if consent given)
        contact_info = None
        if dialogue.consent_share_contact:
            contact = ParticipantContact.query.get(dialogue_id)
            if contact:
                contact_info = json.loads(contact.contact_info)
        
        return {
            'dialogue': dialogue,
            'districts': districts,
            'interest_areas': interest_areas,
            'topics': topics,
            'subtopics': subtopics,
            'contact_info': contact_info
        }
    
    @staticmethod
    def get_dashboard_data():
        """Get dashboard statistics"""
        dialogues = Dialogue.query.all()
        
        total_partners = sum(d.num_people for d in dialogues)
        total_duration = sum(d.duration for d in dialogues)
        
        # Get district statistics
        districts = {}
        for dd in DialogueDistrict.query.all():
            districts[dd.district_name] = districts.get(dd.district_name, 0) + 1
        
        # Get theme statistics from interest areas
        themes = {}
        for dia in DialogueInterestArea.query.all():
            theme = Theme.query.get(dia.interest_area_id)
            if theme:
                themes[theme.name] = themes.get(theme.name, 0) + 1
        
        # Get topic statistics from topic selections
        topics = {}
        for ts in DialogueTopicSelection.query.filter_by(sub_group_id='main').all():
            topic_name = ts.selected_option_id.replace('_', ' ').title()
            topics[topic_name] = topics.get(topic_name, 0) + 1
        
        return {
            'total_dialogues': len(dialogues),
            'total_partners': total_partners,
            'total_duration': total_duration,
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
        
        # Find initiatives that match district and any of the themes
        initiatives = db.session.query(Initiative)\
            .join(InitiativeDistrict, Initiative.id == InitiativeDistrict.initiative_id)\
            .join(InitiativeTheme, Initiative.id == InitiativeTheme.initiative_id)\
            .filter(InitiativeDistrict.district_name == district)\
            .filter(InitiativeTheme.theme_id.in_(theme_ids))\
            .distinct().all()
        
        return initiatives
    
    @staticmethod
    def get_all_themes():
        """Get all available themes"""
        return Theme.query.all()

class UserService:
    """Service for managing users"""
    
    @staticmethod
    def get_or_create_admin():
        """Get or create admin user"""
        user = User.query.filter_by(username='admin').first()
        if not user:
            user = User(username='admin')
            db.session.add(user)
            db.session.commit()
        return user