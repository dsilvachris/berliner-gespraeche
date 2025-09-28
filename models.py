from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Core Tables
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    dialogues = db.relationship('Dialogue', backref='user', lazy=True)

class Theme(db.Model):
    __tablename__ = 'themes'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Initiative(db.Model):
    __tablename__ = 'initiatives'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500), nullable=False)

class Dialogue(db.Model):
    __tablename__ = 'dialogues'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    livable_city = db.Column(db.Text)
    partner_interest = db.Column(db.Text)
    notes = db.Column(db.Text)
    audio_note_url = db.Column(db.String(500))
    observer_reflection = db.Column(db.Text)
    surprise = db.Column(db.Text)
    num_people = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200))
    is_anonymous = db.Column(db.Boolean, nullable=False, default=True)
    consent_share_contact = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class ParticipantContact(db.Model):
    __tablename__ = 'participant_contact'
    
    dialogue_id = db.Column(db.Integer, db.ForeignKey('dialogues.id'), primary_key=True)
    contact_info = db.Column(db.Text, nullable=False)

# Linking Tables
class InitiativeDistrict(db.Model):
    __tablename__ = 'initiative_districts'
    
    initiative_id = db.Column(db.String(50), db.ForeignKey('initiatives.id'), primary_key=True)
    district_name = db.Column(db.String(100), primary_key=True)

class InitiativeTheme(db.Model):
    __tablename__ = 'initiative_themes'
    
    initiative_id = db.Column(db.String(50), db.ForeignKey('initiatives.id'), primary_key=True)
    theme_id = db.Column(db.String(50), db.ForeignKey('themes.id'), primary_key=True)

class DialogueDistrict(db.Model):
    __tablename__ = 'dialogue_districts'
    
    dialogue_id = db.Column(db.Integer, db.ForeignKey('dialogues.id'), primary_key=True)
    district_name = db.Column(db.String(100), primary_key=True)

class DialogueInterestArea(db.Model):
    __tablename__ = 'dialogue_interest_areas'
    
    dialogue_id = db.Column(db.Integer, db.ForeignKey('dialogues.id'), primary_key=True)
    interest_area_id = db.Column(db.String(50), db.ForeignKey('themes.id'), primary_key=True)

class DialogueTopicSelection(db.Model):
    __tablename__ = 'dialogue_topic_selections'
    
    id = db.Column(db.Integer, primary_key=True)
    dialogue_id = db.Column(db.Integer, db.ForeignKey('dialogues.id'), nullable=False)
    main_topic_id = db.Column(db.String(50), nullable=False)
    sub_group_id = db.Column(db.String(50), nullable=False)
    selected_option_id = db.Column(db.String(50), nullable=False)
    custom_note = db.Column(db.Text)