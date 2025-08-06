#!/usr/bin/env python3
"""
Fix CSV export to include all data from normalized schema
"""

def fix_csv_export():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the CSV export function
    old_csv_function = """@app.route('/export/csv')
def export_csv():
    dialogues = Dialogue.query.order_by(Dialogue.created_at.desc()).all()
    
    data = []
    for d in dialogues:
        data.append({
            'ID': d.id,
            'Timestamp': d.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Notes': d.notes or '',
            'Observer Reflection': d.observer_reflection or '',
            'Num People': d.num_people,
            'Duration': d.duration,
            'Anonymous': d.is_anonymous,
            'Consent Share Contact': d.consent_share_contact
        })
    
    df = pd.DataFrame(data)
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=berliner_gespraeche_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response"""
    
    new_csv_function = """@app.route('/export/csv')
def export_csv():
    dialogues = Dialogue.query.order_by(Dialogue.created_at.desc()).all()
    
    data = []
    for d in dialogues:
        # Get districts
        districts = [dd.district_name for dd in DialogueDistrict.query.filter_by(dialogue_id=d.id)]
        
        # Get interest areas
        interest_areas = []
        for dia in DialogueInterestArea.query.filter_by(dialogue_id=d.id):
            theme = Theme.query.get(dia.interest_area_id)
            if theme:
                interest_areas.append(theme.name)
        
        # Get topics
        topics = []
        for ts in DialogueTopicSelection.query.filter_by(dialogue_id=d.id, sub_group_id='main'):
            topics.append(ts.selected_option_id.replace('_', ' ').title())
        
        # Get subtopics
        subtopics = []
        for ts in DialogueTopicSelection.query.filter_by(dialogue_id=d.id, sub_group_id='detail'):
            subtopics.append(ts.selected_option_id.replace('_', ' ').title())
        
        # Get contact info if available
        contact_info = {}
        if d.consent_share_contact:
            contact = ParticipantContact.query.get(d.id)
            if contact:
                import json
                contact_info = json.loads(contact.contact_info)
        
        data.append({
            'ID': d.id,
            'Timestamp': d.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Districts': ', '.join(districts),
            'Interest Areas': ', '.join(interest_areas),
            'Topics': ', '.join(topics),
            'Subtopics': ', '.join(subtopics),
            'Notes': d.notes or '',
            'Observer Reflection': d.observer_reflection or '',
            'Num People': d.num_people,
            'Duration': d.duration,
            'Anonymous': d.is_anonymous,
            'Consent Share Contact': d.consent_share_contact,
            'Name': contact_info.get('name', '') if contact_info else '',
            'Email': contact_info.get('email', '') if contact_info else '',
            'Phone': contact_info.get('phone', '') if contact_info else '',
            'Family Status': contact_info.get('family_status', '') if contact_info else ''
        })
    
    df = pd.DataFrame(data)
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=berliner_gespraeche_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response"""
    
    content = content.replace(old_csv_function, new_csv_function)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("CSV export fixed")

if __name__ == '__main__':
    fix_csv_export()