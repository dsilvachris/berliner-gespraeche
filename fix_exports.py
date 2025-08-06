#!/usr/bin/env python3
"""
Fix export routes to work with new database schema
"""

def fix_export_routes():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace export routes with new schema compatible versions
    old_excel_route = """@app.route('/export/excel')
def export_excel():
    dialogues = Dialogue.query.order_by(Dialogue.created_at.desc()).all()
    
    data = []
    for d in dialogues:
        data.append({
            'ID': d.id,
            'Timestamp': d.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Lebenswerte Stadt': d.livable_city,
            'Partner Interesse': d.partner_interest,
            'Themen': ', '.join(d.topics) if d.topics else '',
            'Notizen': d.notes,
            'Bezirk': d.district,
            'Initiativen': ', '.join(d.initiatives) if d.initiatives else '',
            'Reflexion': d.reflection,
            'Anzahl Personen': d.num_people,
            'Dauer (Min)': d.duration,
            'Email': d.email,
            'Telefon': d.phone,
            'Einverständnis': d.consent,
            'Datenschutz': d.data_protection
        })"""
    
    new_excel_route = """@app.route('/export/excel')
def export_excel():
    from services import DialogueService
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
        })"""
    
    content = content.replace(old_excel_route, new_excel_route)
    
    # Fix CSV route similarly
    old_csv_data = """    data = []
    for d in dialogues:
        data.append({
            'ID': d.id,
            'Timestamp': d.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Lebenswerte Stadt': d.livable_city,
            'Partner Interesse': d.partner_interest,
            'Themen': ', '.join(d.topics) if d.topics else '',
            'Notizen': d.notes,
            'Bezirk': d.district,
            'Initiativen': ', '.join(d.initiatives) if d.initiatives else '',
            'Reflexion': d.reflection,
            'Anzahl Personen': d.num_people,
            'Dauer (Min)': d.duration,
            'Email': d.email,
            'Telefon': d.phone,
            'Einverständnis': d.consent,
            'Datenschutz': d.data_protection
        })"""
    
    new_csv_data = """    data = []
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
        })"""
    
    content = content.replace(old_csv_data, new_csv_data)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Export routes fixed")

if __name__ == '__main__':
    fix_export_routes()