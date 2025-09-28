#!/usr/bin/env python3
"""
Database Migration Script
Migrates from old flat structure to new normalized schema
"""

import json
from datetime import datetime
from models import *
from app import app

# Theme mappings
THEME_MAPPINGS = {
    'Urban Garden': 'urban_garden',
    'Repair Café': 'repair_cafe', 
    'Climate Education': 'climate_education',
    'Policy Advocacy': 'policy_advocacy',
    'Mutual Aid': 'mutual_aid',
    'Digital Inclusion': 'digital_inclusion'
}

def populate_themes():
    """Populate themes table with predefined themes"""
    themes_data = [
        ('urban_garden', 'Urban Garden', 'Community gardens and urban farming initiatives'),
        ('repair_cafe', 'Repair Café', 'Community repair workshops and circular economy'),
        ('climate_education', 'Climate Education', 'Environmental education and awareness programs'),
        ('policy_advocacy', 'Policy Advocacy', 'Climate policy and advocacy initiatives'),
        ('mutual_aid', 'Mutual Aid', 'Community support and solidarity networks'),
        ('digital_inclusion', 'Digital Inclusion', 'Digital literacy and inclusion programs')
    ]
    
    for theme_id, name, description in themes_data:
        if not Theme.query.get(theme_id):
            theme = Theme(id=theme_id, name=name, description=description)
            db.session.add(theme)
    
    db.session.commit()
    print("Themes populated")

def populate_initiatives():
    """Populate initiatives from existing INITIATIVES_DATA"""
    from app import INITIATIVES_DATA
    
    for district, categories in INITIATIVES_DATA.items():
        for category, initiatives in categories.items():
            theme_id = THEME_MAPPINGS.get(category)
            if not theme_id:
                continue
                
            for init_name, init_data in initiatives.items():
                # Create unique initiative ID
                init_id = f"{district.lower().replace(' ', '_')}_{init_name.lower().replace(' ', '_')}"
                
                if not Initiative.query.get(init_id):
                    initiative = Initiative(
                        id=init_id,
                        name=init_name,
                        description=init_data['summary'],
                        link=init_data['contact']
                    )
                    db.session.add(initiative)
                    
                    # Link to district
                    district_link = InitiativeDistrict(
                        initiative_id=init_id,
                        district_name=district
                    )
                    db.session.add(district_link)
                    
                    # Link to theme
                    theme_link = InitiativeTheme(
                        initiative_id=init_id,
                        theme_id=theme_id
                    )
                    db.session.add(theme_link)
    
    db.session.commit()
    print("Initiatives populated")

def create_default_user():
    """Create default admin user"""
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin')
        db.session.add(user)
        db.session.commit()
        print("Default admin user created")
        return user.id
    else:
        return User.query.filter_by(username='admin').first().id

def migrate_old_dialogues():
    """Migrate existing dialogues from old schema"""
    # Import old model
    from app import Dialogue as OldDialogue
    
    admin_user_id = create_default_user()
    old_dialogues = OldDialogue.query.all()
    
    for old_dialogue in old_dialogues:
        # Create new dialogue
        new_dialogue = Dialogue(
            user_id=admin_user_id,
            notes=old_dialogue.notes or '',
            observer_reflection=old_dialogue.reflection or '',
            num_people=old_dialogue.num_people or 1,
            duration=old_dialogue.duration or 0,
            is_anonymous=old_dialogue.consent != 'yes',
            consent_share_contact=old_dialogue.consent == 'yes',
            created_at=old_dialogue.timestamp or datetime.utcnow()
        )
        db.session.add(new_dialogue)
        db.session.flush()  # Get the ID
        
        # Add district
        if old_dialogue.district:
            district_link = DialogueDistrict(
                dialogue_id=new_dialogue.id,
                district_name=old_dialogue.district
            )
            db.session.add(district_link)
        
        # Add interest areas (from initiative_types)
        if hasattr(old_dialogue, 'initiatives') and old_dialogue.initiatives:
            try:
                initiatives = json.loads(old_dialogue.initiatives) if isinstance(old_dialogue.initiatives, str) else old_dialogue.initiatives
                for init in initiatives:
                    # Try to map initiative to theme
                    for theme_name, theme_id in THEME_MAPPINGS.items():
                        if theme_name.lower() in init.lower():
                            interest_link = DialogueInterestArea(
                                dialogue_id=new_dialogue.id,
                                interest_area_id=theme_id
                            )
                            db.session.add(interest_link)
                            break
            except:
                pass
        
        # Add topic selections (from topics and subtopics)
        if hasattr(old_dialogue, 'topics') and old_dialogue.topics:
            try:
                topics = json.loads(old_dialogue.topics) if isinstance(old_dialogue.topics, str) else old_dialogue.topics
                subtopics = json.loads(old_dialogue.subtopics) if hasattr(old_dialogue, 'subtopics') and old_dialogue.subtopics else []
                
                for topic in topics:
                    topic_selection = DialogueTopicSelection(
                        dialogue_id=new_dialogue.id,
                        main_topic_id=topic.lower().replace('/', '_').replace(' ', '_'),
                        sub_group_id='general',
                        selected_option_id=topic.lower().replace('/', '_').replace(' ', '_')
                    )
                    db.session.add(topic_selection)
                
                for subtopic in subtopics:
                    subtopic_selection = DialogueTopicSelection(
                        dialogue_id=new_dialogue.id,
                        main_topic_id='subtopic',
                        sub_group_id='detail',
                        selected_option_id=subtopic.lower().replace(' ', '_')
                    )
                    db.session.add(subtopic_selection)
            except:
                pass
        
        # Add contact info if consent given
        if old_dialogue.consent == 'yes' and (old_dialogue.email or old_dialogue.phone):
            contact_info = {
                'name': f"{old_dialogue.name or ''} {old_dialogue.surname or ''}".strip(),
                'email': old_dialogue.email or '',
                'phone': old_dialogue.phone or '',
                'data_protection': old_dialogue.data_protection or ''
            }
            
            participant_contact = ParticipantContact(
                dialogue_id=new_dialogue.id,
                contact_info=json.dumps(contact_info)
            )
            db.session.add(participant_contact)
    
    db.session.commit()
    print(f"Migrated {len(old_dialogues)} dialogues")

def run_migration():
    """Run complete migration"""
    print("Starting database migration...")
    
    with app.app_context():
        # Create all new tables
        db.create_all()
        print("New tables created")
        
        # Populate reference data
        populate_themes()
        populate_initiatives()
        
        # Migrate existing data
        migrate_old_dialogues()
        
        print("Migration completed successfully!")

if __name__ == '__main__':
    run_migration()