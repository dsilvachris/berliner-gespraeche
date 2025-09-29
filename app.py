from flask import Flask, render_template, request, redirect, url_for, session, send_file, make_response
import qrcode
import io
import base64
from datetime import datetime
import pandas as pd
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from database import db, setup_database
from dotenv import load_dotenv
import socket

load_dotenv()

app = Flask(__name__)
app.secret_key = 'berliner_gespraeche_secret_key'

# Subtopics data
SUBTOPICS_DATA = {
    'Wohnen/Bauwende': ['Affordability', 'Social Housing', 'Gentrification', 'Energy Efficiency', 'Renovation'],
    'Mobilität': ['Cycle', 'Bicycle', 'Electric Car', 'Parking', 'Public Transport (ÖPNV)', 'Health (Accidents, Air Quality)'],
    'Klimaanpassung': ['Heat', 'Heavy Rain', 'Trees'],
    'Food': ['Local Production', 'Organic', 'Food Waste', 'Urban Farming', 'Sustainable Diet'],
    'Building Transition': ['Concrete', 'Waste', 'Costs', 'Rent', 'Existing Stock', 'Community', 'Quality Of Life', 'Displacement', 'Wood'],
    'Heating Transition': ['Openness to Technology', 'Economically Unviable', 'Rent Increase', 'Costs', 'Monument Protection', 'District Heating', 'Old Building', 'Homeownership']
}

# Initiative data
INITIATIVES_DATA = {
    'Mitte': {
        'Urban Garden': {
            'Prinzessinnengarten': {
                'contact': 'info@prinzessinnengarten.net, +49 30 12345678',
                'summary': 'Community garden promoting urban agriculture and sustainability.'
            }
        },
        'Repair Café': {
            'Repair Café Mitte': {
                'contact': 'mitte@repaircafe-berlin.de, +49 30 11111111',
                'summary': 'Free repair service for electronics and household items.'
            }
        },
        'Climate Education': {
            'Klimawerkstatt Berlin': {
                'contact': 'info@klimawerkstatt.berlin, +49 30 33333333',
                'summary': 'Educational workshops on climate change and sustainability.'
            }
        }
    },
    'Neukölln': {
        'Urban Garden': {
            'Tempelhofer Feld Gärten': {
                'contact': 'tempelhof@garden.de, +49 30 12345678',
                'summary': 'Community garden at Tempelhof Field promoting urban agriculture.'
            }
        },
        'Repair Café': {
            'Repair Café Neukölln': {
                'contact': 'neukoelln@repaircafe.de, +49 30 11111111',
                'summary': 'Community repair service in Neukölln for electronics and household items.'
            }
        }
    }
}

# Add other districts
for district in ['Kreuzberg', 'Prenzlauer Berg', 'Charlottenburg', 'Friedrichshain', 'Schöneberg', 'Wedding', 'Tempelhof', 'Steglitz']:
    INITIATIVES_DATA[district] = {
        'Urban Garden': {
            f'{district} Community Garden': {
                'contact': f'{district.lower().replace(" ", "")}@garden.de, +49 30 12345678',
                'summary': f'Local community garden in {district} promoting sustainable urban agriculture.'
            }
        },
        'Repair Café': {
            f'Repair Café {district}': {
                'contact': f'{district.lower().replace(" ", "")}@repaircafe.de, +49 30 11111111',
                'summary': f'Community repair service in {district} for electronics and household items.'
            }
        }
    }

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'Admin' and password == 'Admin123':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Ungültige Anmeldedaten')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/start')
def start_dialogue():
    dialogue_keys = [k for k in session.keys() if k not in ['logged_in', 'last_dialogue_id']]
    for key in dialogue_keys:
        session.pop(key, None)
    return render_template('step1.html')

@app.route('/step1', methods=['POST'])
def step1():
    session['livable_city'] = request.form.get('livable_city', '')
    session['partner_interest'] = request.form.get('partner_interest', '')
    return redirect(url_for('step2'))

@app.route('/step2')
def step2():
    return render_template('step2.html', subtopics_data=SUBTOPICS_DATA)

@app.route('/step2', methods=['POST'])
def step2_post():
    session['topics'] = request.form.getlist('topics')
    session['subtopics'] = request.form.getlist('subtopics')
    session['notes'] = request.form.get('notes', '')
    session['district'] = request.form.get('district', '')
    return redirect(url_for('step3'))

@app.route('/step3')
def step3():
    district = session.get('district', '')
    return render_template('step3.html', district=district, initiatives_data=INITIATIVES_DATA)

@app.route('/step3', methods=['POST'])
def step3_post():
    if 'skip_step' in request.form:
        session['initiative_types'] = []
        session['selected_initiatives'] = []
        return redirect(url_for('step4'))
    
    session['initiative_types'] = request.form.getlist('initiative_types')
    session['selected_initiatives'] = request.form.getlist('selected_initiatives')
    
    if 'show_qr' in request.form:
        return redirect(url_for('contact_info'))
    else:
        return redirect(url_for('step4'))

@app.route('/contact_info')
def contact_info():
    selected_initiatives = session.get('selected_initiatives', [])
    initiative_types = session.get('initiative_types', [])
    district = session.get('district', '')
    
    if not selected_initiatives and initiative_types and district in INITIATIVES_DATA:
        selected_initiatives = []
        for init_type in initiative_types:
            if init_type in INITIATIVES_DATA[district]:
                first_initiative = list(INITIATIVES_DATA[district][init_type].keys())[0]
                selected_initiatives.append(first_initiative)
    
    # Store contact info in database for QR access
    contact_id = db.execute_one(
        "INSERT INTO contact_shares (district, initiatives) VALUES (%s, %s) RETURNING id",
        (district, selected_initiatives)
    )['id']
    
    # Get detailed initiative info
    initiative_details = []
    if selected_initiatives and district in INITIATIVES_DATA:
        for initiative in selected_initiatives:
            for category, initiatives in INITIATIVES_DATA[district].items():
                if initiative in initiatives:
                    initiative_details.append({
                        'name': initiative,
                        'contact': initiatives[initiative]['contact'],
                        'summary': initiatives[initiative]['summary']
                    })
                    break
    
    # Generate QR code
    host = request.host
    if 'localhost' in host or '127.0.0.1' in host:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            network_ip = s.getsockname()[0]
            s.close()
            qr_url = f"http://{network_ip}:5001/public_contact/{contact_id}"
        except:
            qr_url = f"http://{host}/public_contact/{contact_id}"
    else:
        qr_url = f"http://{host}/public_contact/{contact_id}"
    
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('contact_info.html', 
                         initiative_details=initiative_details,
                         district=district,
                         qr_code=qr_code,
                         contact_url=qr_url)

@app.route('/public_contact/<int:contact_id>')
def public_contact(contact_id):
    contact_share = db.execute_one(
        "SELECT district, initiatives FROM contact_shares WHERE id = %s",
        (contact_id,)
    )
    
    if not contact_share:
        return render_template('contact_info.html', 
                             initiative_details=[],
                             district='Unknown',
                             qr_code=None,
                             error="Contact information not found",
                             public_view=True)
    
    selected_initiatives = contact_share['initiatives']
    district = contact_share['district']
    
    initiative_details = []
    if selected_initiatives and district in INITIATIVES_DATA:
        for initiative in selected_initiatives:
            for category, initiatives in INITIATIVES_DATA[district].items():
                if initiative in initiatives:
                    initiative_details.append({
                        'name': initiative,
                        'contact': initiatives[initiative]['contact'],
                        'summary': initiatives[initiative]['summary']
                    })
                    break
    
    return render_template('contact_info.html', 
                         initiative_details=initiative_details,
                         district=district,
                         qr_code=None,
                         public_view=True)

@app.route('/step4')
def step4():
    return render_template('step4.html')

@app.route('/step4', methods=['POST'])
def step4_post():
    session['name'] = request.form.get('name', '')
    session['surname'] = request.form.get('surname', '')
    session['email'] = request.form.get('email', '')
    session['phone'] = request.form.get('phone', '')
    session['consent'] = request.form.get('consent', '') == 'on'
    session['data_protection'] = request.form.get('data_protection', '') == 'on'
    return redirect(url_for('step5'))

@app.route('/step5')
def step5():
    return render_template('step5.html')

@app.route('/step5', methods=['POST'])
def step5_post():
    session['reflection'] = request.form.get('reflection', '')
    session['num_people'] = int(request.form.get('num_people', '1'))
    session['duration'] = int(request.form.get('duration', '0'))
    session['family_status'] = request.form.get('family_status', '')
    return redirect(url_for('review'))

@app.route('/review')
def review():
    return render_template('review.html')

@app.route('/review', methods=['POST'])
def review_post():
    session['livable_city'] = request.form.get('livable_city', '')
    session['partner_interest'] = request.form.get('partner_interest', '')
    session['notes'] = request.form.get('notes', '')
    session['district'] = request.form.get('district', '')
    session['name'] = request.form.get('name', '')
    session['surname'] = request.form.get('surname', '')
    session['email'] = request.form.get('email', '')
    session['phone'] = request.form.get('phone', '')
    
    return redirect(url_for('complete_dialogue'))

@app.route('/complete')
def complete_dialogue():
    # Get admin user
    admin_user = db.execute_one("SELECT id FROM users WHERE username = %s", ('Admin',))
    
    # Create dialogue
    dialogue_id = db.execute_one("""
        INSERT INTO dialogues (
            user_id, livable_city, partner_interest, notes, district,
            topics, subtopics, initiative_types, selected_initiatives,
            name, surname, email, phone, consent, data_protection,
            reflection, num_people, duration, family_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        admin_user['id'],
        session.get('livable_city', ''),
        session.get('partner_interest', ''),
        session.get('notes', ''),
        session.get('district', ''),
        session.get('topics', []),
        session.get('subtopics', []),
        session.get('initiative_types', []),
        session.get('selected_initiatives', []),
        session.get('name', ''),
        session.get('surname', ''),
        session.get('email', ''),
        session.get('phone', ''),
        session.get('consent', False),
        session.get('data_protection', False),
        session.get('reflection', ''),
        session.get('num_people', 1),
        session.get('duration', 0),
        session.get('family_status', '')
    ))['id']
    
    session.clear()
    session['last_dialogue_id'] = dialogue_id
    
    return render_template('thank_you.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Get dashboard statistics
    total_dialogues = db.execute_one("SELECT COUNT(*) as count FROM dialogues")['count']
    
    dialogues = db.execute("""
        SELECT id, created_at, district, topics, num_people, duration, name, email
        FROM dialogues 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    
    # Calculate total partners and duration
    totals = db.execute_one("""
        SELECT 
            COALESCE(SUM(num_people), 0) as total_partners,
            COALESCE(SUM(duration), 0) as total_duration
        FROM dialogues
    """)
    
    # Get district statistics
    district_stats = db.execute("""
        SELECT district, COUNT(*) as count 
        FROM dialogues 
        WHERE district IS NOT NULL AND district != ''
        GROUP BY district 
        ORDER BY count DESC
    """)
    
    # Get topic statistics
    topic_stats = db.execute("""
        SELECT unnest(topics) as topic, COUNT(*) as count 
        FROM dialogues 
        WHERE topics IS NOT NULL AND array_length(topics, 1) > 0
        GROUP BY topic 
        ORDER BY count DESC 
        LIMIT 10
    """)
    
    # Convert to dictionaries for charts
    districts_dict = {row['district']: row['count'] for row in district_stats}
    topics_dict = {row['topic']: row['count'] for row in topic_stats}
    
    dashboard_data = {
        'total_dialogues': total_dialogues,
        'total_partners': totals['total_partners'],
        'total_duration': totals['total_duration'],
        'districts': districts_dict,
        'topics': topics_dict
    }
    
    return render_template('dashboard.html', data=dashboard_data, dialogues=dialogues)

@app.route('/export/csv')
def export_csv():
    dialogues = db.execute("""
        SELECT id, created_at, livable_city, partner_interest, notes, district,
               topics, subtopics, initiative_types, selected_initiatives,
               name, surname, email, phone, consent, data_protection,
               reflection, num_people, duration, family_status
        FROM dialogues 
        ORDER BY created_at DESC
    """)
    
    data = []
    for d in dialogues:
        data.append({
            'ID': d['id'],
            'Timestamp': d['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'Livable City': d['livable_city'] or '',
            'Partner Interest': d['partner_interest'] or '',
            'Notes': d['notes'] or '',
            'District': d['district'] or '',
            'Topics': ', '.join(d['topics'] or []),
            'Subtopics': ', '.join(d['subtopics'] or []),
            'Initiative Types': ', '.join(d['initiative_types'] or []),
            'Selected Initiatives': ', '.join(d['selected_initiatives'] or []),
            'Name': d['name'] if d['consent'] else '',
            'Email': d['email'] if d['consent'] else '',
            'Phone': d['phone'] if d['consent'] else '',
            'Reflection': d['reflection'] or '',
            'Num People': d['num_people'] or 0,
            'Duration': d['duration'] or 0,
            'Family Status': d['family_status'] or ''
        })
    
    df = pd.DataFrame(data)
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=berliner_gespraeche_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/export/excel')
def export_excel():
    dialogues = db.execute("""
        SELECT id, created_at, livable_city, partner_interest, notes, district,
               topics, subtopics, initiative_types, selected_initiatives,
               name, surname, email, phone, consent, data_protection,
               reflection, num_people, duration, family_status
        FROM dialogues 
        ORDER BY created_at DESC
    """)
    
    data = []
    for d in dialogues:
        data.append({
            'ID': d['id'],
            'Timestamp': d['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'Livable City': d['livable_city'] or '',
            'Partner Interest': d['partner_interest'] or '',
            'Notes': d['notes'] or '',
            'District': d['district'] or '',
            'Topics': ', '.join(d['topics'] or []),
            'Subtopics': ', '.join(d['subtopics'] or []),
            'Initiative Types': ', '.join(d['initiative_types'] or []),
            'Selected Initiatives': ', '.join(d['selected_initiatives'] or []),
            'Name': d['name'] if d['consent'] else '',
            'Email': d['email'] if d['consent'] else '',
            'Phone': d['phone'] if d['consent'] else '',
            'Reflection': d['reflection'] or '',
            'Num People': d['num_people'] or 0,
            'Duration': d['duration'] or 0,
            'Family Status': d['family_status'] or ''
        })
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Berliner Gespräche')
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'berliner_gespraeche_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/download_dialogue_pdf')
def download_dialogue_pdf():
    dialogue_id = session.get('last_dialogue_id')
    if not dialogue_id:
        return redirect(url_for('index'))
    
    dialogue = db.execute_one("SELECT * FROM dialogues WHERE id = %s", (dialogue_id,))
    if not dialogue:
        return redirect(url_for('index'))
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30)
    story.append(Paragraph("Sag doch mal, Berlin - Dialog Zusammenfassung", title_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>Datum:</b> {dialogue['created_at'].strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    story.append(Paragraph(f"<b>Bezirk:</b> {dialogue['district'] or 'Nicht angegeben'}", styles['Normal']))
    story.append(Paragraph(f"<b>Anzahl Personen:</b> {dialogue['num_people']}", styles['Normal']))
    story.append(Paragraph(f"<b>Dauer:</b> {dialogue['duration']} Minuten", styles['Normal']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>1. Lebenswerte Stadt:</b>", styles['Heading2']))
    story.append(Paragraph(dialogue['livable_city'] or 'Keine Angabe', styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Dialogpartner Interesse:</b>", styles['Heading2']))
    story.append(Paragraph(dialogue['partner_interest'] or 'Keine Angabe', styles['Normal']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>2. Diskutierte Themen:</b>", styles['Heading2']))
    topics_text = ', '.join(dialogue['topics'] or []) if dialogue['topics'] else 'Keine Themen ausgewählt'
    story.append(Paragraph(topics_text, styles['Normal']))
    if dialogue['subtopics']:
        subtopics_text = ', '.join(dialogue['subtopics'])
        story.append(Paragraph(f"<b>Unterthemen:</b> {subtopics_text}", styles['Normal']))
    if dialogue['notes']:
        story.append(Paragraph(f"<b>Notizen:</b> {dialogue['notes']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if dialogue['reflection']:
        story.append(Paragraph("<b>3. Reflexion:</b>", styles['Heading2']))
        story.append(Paragraph(dialogue['reflection'], styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        io.BytesIO(buffer.read()),
        as_attachment=True,
        download_name=f'dialog_{dialogue["id"]}_{dialogue["created_at"].strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    try:
        setup_database()
    except Exception as e:
        print(f"Database setup warning: {e}")
        print("Make sure PostgreSQL is running and database 'berliner_gespraeche' exists")
    
    print("\n" + "="*50)
    print("PostgreSQL Berliner Gespräche Server starting...")
    print("Database: PostgreSQL (berliner_gespraeche)")
    print("For mobile access, use your network IP:")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        network_ip = s.getsockname()[0]
        s.close()
        print(f"   http://{network_ip}:5001")
    except:
        print("   Network IP detection failed")
    
    print("For local access: http://localhost:5001")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)