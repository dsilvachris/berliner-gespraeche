"""
REST API Routes for Klimaneustart Civic Dialogue App
Implements the API specification from apis.md
"""

from flask import Blueprint, jsonify, request
from models import *
from services import DialogueService, InitiativeService, UserService
import json

# Create API blueprint
api = Blueprint('api', __name__, url_prefix='/api/v1')

# 3.1 Lookup Endpoints (Read-Only)

@api.route('/lookup/themes', methods=['GET'])
def get_all_themes():
    """Get all available interest areas/themes"""
    themes = Theme.query.all()
    return jsonify([{
        'id': theme.id,
        'name': theme.name,
        'description': theme.description or ''
    } for theme in themes])

@api.route('/lookup/initiatives', methods=['GET'])
def get_all_initiatives():
    """Get all initiatives with associated districts and themes"""
    initiatives = Initiative.query.all()
    result = []
    
    for initiative in initiatives:
        # Get districts for this initiative
        districts = [id.district_name for id in InitiativeDistrict.query.filter_by(initiative_id=initiative.id)]
        
        # Get themes for this initiative
        themes = []
        for it in InitiativeTheme.query.filter_by(initiative_id=initiative.id):
            theme = Theme.query.get(it.theme_id)
            if theme:
                themes.append(theme.name)
        
        result.append({
            'id': initiative.id,
            'name': initiative.name,
            'description': initiative.description,
            'districts': districts,
            'themes': themes
        })
    
    return jsonify(result)

@api.route('/lookup/topics', methods=['GET'])
def get_all_topics():
    """Get complete hierarchical topic structure"""
    # Define the topic structure based on existing SUBTOPICS_DATA
    topics = [
        {
            'id': 'wohnen_bauwende',
            'name': 'Wohnen/Bauwende',
            'subGroups': [
                {
                    'id': 'housing',
                    'name': 'Housing',
                    'options': [
                        {'id': 'affordability', 'name': 'Affordability'},
                        {'id': 'social_housing', 'name': 'Social Housing'},
                        {'id': 'gentrification', 'name': 'Gentrification'},
                        {'id': 'energy_efficiency', 'name': 'Energy Efficiency'},
                        {'id': 'renovation', 'name': 'Renovation'}
                    ]
                }
            ]
        },
        {
            'id': 'mobilitaet',
            'name': 'Mobilität',
            'subGroups': [
                {
                    'id': 'transport',
                    'name': 'Transport',
                    'options': [
                        {'id': 'cycle', 'name': 'Cycle'},
                        {'id': 'bicycle', 'name': 'Bicycle'},
                        {'id': 'electric_car', 'name': 'Electric Car'},
                        {'id': 'parking', 'name': 'Parking'},
                        {'id': 'public_transport', 'name': 'Public Transport'},
                        {'id': 'health_accidents_air_quality', 'name': 'Health (Accidents, Air Quality)'}
                    ]
                }
            ]
        },
        {
            'id': 'klimaanpassung',
            'name': 'Klimaanpassung',
            'subGroups': [
                {
                    'id': 'climate',
                    'name': 'Climate',
                    'options': [
                        {'id': 'heat', 'name': 'Heat'},
                        {'id': 'heavy_rain', 'name': 'Heavy Rain'},
                        {'id': 'trees', 'name': 'Trees'}
                    ]
                }
            ]
        },
        {
            'id': 'food',
            'name': 'Food',
            'subGroups': [
                {
                    'id': 'food_systems',
                    'name': 'Food Systems',
                    'options': [
                        {'id': 'local_production', 'name': 'Local Production'},
                        {'id': 'organic', 'name': 'Organic'},
                        {'id': 'food_waste', 'name': 'Food Waste'},
                        {'id': 'urban_farming', 'name': 'Urban Farming'},
                        {'id': 'sustainable_diet', 'name': 'Sustainable Diet'}
                    ]
                }
            ]
        },
        {
            'id': 'building_transition',
            'name': 'Building Transition',
            'subGroups': [
                {
                    'id': 'construction',
                    'name': 'Construction',
                    'options': [
                        {'id': 'concrete', 'name': 'Concrete'},
                        {'id': 'waste', 'name': 'Waste'},
                        {'id': 'costs', 'name': 'Costs'},
                        {'id': 'rent', 'name': 'Rent'},
                        {'id': 'existing_stock', 'name': 'Existing Stock'},
                        {'id': 'community', 'name': 'Community'},
                        {'id': 'quality_of_life', 'name': 'Quality Of Life'},
                        {'id': 'displacement', 'name': 'Displacement'},
                        {'id': 'wood', 'name': 'Wood'}
                    ]
                }
            ]
        },
        {
            'id': 'heating_transition',
            'name': 'Heating Transition',
            'subGroups': [
                {
                    'id': 'heating',
                    'name': 'Heating',
                    'options': [
                        {'id': 'openness_to_technology', 'name': 'Openness to Technology'},
                        {'id': 'economically_unviable', 'name': 'Economically Unviable'},
                        {'id': 'rent_increase', 'name': 'Rent Increase'},
                        {'id': 'costs', 'name': 'Costs'},
                        {'id': 'monument_protection', 'name': 'Monument Protection'},
                        {'id': 'district_heating', 'name': 'District Heating'},
                        {'id': 'old_building', 'name': 'Old Building'},
                        {'id': 'homeownership', 'name': 'Homeownership'}
                    ]
                }
            ]
        }
    ]
    
    return jsonify(topics)

@api.route('/lookup/districts', methods=['GET'])
def get_all_districts():
    """Get list of Berlin districts"""
    districts = [
        'Mitte', 'Neukölln', 'Kreuzberg', 'Prenzlauer Berg', 
        'Charlottenburg', 'Friedrichshain', 'Schöneberg', 
        'Wedding', 'Tempelhof', 'Steglitz'
    ]
    return jsonify(districts)

# 3.2 Data Ingestion Endpoints (Write)

@api.route('/initiatives', methods=['POST'])
def create_initiative():
    """Create a new initiative"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 422
        
        # Validate required fields
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 422
        
        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = data['name'].lower().replace(' ', '_').replace('/', '_')
        
        # Create initiative
        initiative = Initiative(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            link=data.get('link', '')
        )
        
        db.session.add(initiative)
        
        # Add district associations
        if 'districts' in data:
            for district in data['districts']:
                district_link = InitiativeDistrict(
                    initiative_id=initiative.id,
                    district_name=district
                )
                db.session.add(district_link)
        
        # Add theme associations
        if 'themes' in data:
            for theme_name in data['themes']:
                # Find theme by name
                theme = Theme.query.filter_by(name=theme_name).first()
                if theme:
                    theme_link = InitiativeTheme(
                        initiative_id=initiative.id,
                        theme_id=theme.id
                    )
                    db.session.add(theme_link)
        
        db.session.commit()
        
        return jsonify({
            'id': initiative.id,
            'name': initiative.name,
            'description': initiative.description,
            'districts': data.get('districts', []),
            'themes': data.get('themes', [])
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/dialogues', methods=['POST'])
def submit_dialogue():
    """Submit a complete dialogue session"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 422
        
        # Get admin user
        admin_user = UserService.get_or_create_admin()
        
        # Start database transaction
        db.session.begin()
        
        # Create main dialogue record
        dialogue = Dialogue(
            user_id=admin_user.id,
            livable_city=data.get('livableCity', ''),
            partner_interest=data.get('mainInterest', ''),
            notes=data.get('notes', ''),
            observer_reflection=data.get('observerReflection', ''),
            surprise=data.get('surprise', ''),
            num_people=int(data.get('numPeople', 1)),
            duration=int(data.get('duration', 0)),
            is_anonymous=data.get('isAnonymous', True),
            consent_share_contact=data.get('shareContact', False)
        )
        
        db.session.add(dialogue)
        db.session.flush()  # Get the ID
        
        # Add districts
        for district in data.get('districts', []):
            district_link = DialogueDistrict(
                dialogue_id=dialogue.id,
                district_name=district
            )
            db.session.add(district_link)
        
        # Add interest areas
        for interest_area in data.get('interestAreas', []):
            # Find theme by name
            theme = Theme.query.filter_by(name=interest_area).first()
            if theme:
                interest_link = DialogueInterestArea(
                    dialogue_id=dialogue.id,
                    interest_area_id=theme.id
                )
                db.session.add(interest_link)
        
        # Add topic selections
        topic_details = data.get('topicDetails', {})
        for main_topic_id, sub_groups in topic_details.items():
            for sub_group_id, sub_group_data in sub_groups.items():
                selected_options = sub_group_data.get('selectedOptions', [])
                custom_note = sub_group_data.get('customNote', '')
                
                for option_id in selected_options:
                    topic_selection = DialogueTopicSelection(
                        dialogue_id=dialogue.id,
                        main_topic_id=main_topic_id,
                        sub_group_id=sub_group_id,
                        selected_option_id=option_id,
                        custom_note=custom_note
                    )
                    db.session.add(topic_selection)
        
        # Handle contact info (only if consent given)
        if data.get('shareContact', False) and data.get('contactInfo'):
            contact_info = data['contactInfo']
            participant_contact = ParticipantContact(
                dialogue_id=dialogue.id,
                contact_info=json.dumps(contact_info)
            )
            db.session.add(participant_contact)
        
        # Commit transaction
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Dialogue created successfully.',
            'dialogue_id': dialogue.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405