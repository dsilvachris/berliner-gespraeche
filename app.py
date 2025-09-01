from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, make_response
import qrcode
import io
import base64
from datetime import datetime
import json
import os
import pandas as pd
import tempfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from mongo_models import *
from mongo_services import *
from bson import ObjectId

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'berliner_gespraeche_secret_key')

@app.route('/')
def root():
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

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

@app.route('/start')
def start_dialogue():
    # Clear dialogue session
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

# Subtopics data
SUBTOPICS_DATA = {
    'Wohnen/Bauwende': ['Affordability', 'Social Housing', 'Gentrification', 'Energy Efficiency', 'Renovation'],
    'Mobilität': ['Cycle', 'Bicycle', 'Electric Car', 'Parking', 'Public Transport (ÖPNV)', 'Health (Accidents, Air Quality)'],
    'Klimaanpassung': ['Heat', 'Heavy Rain', 'Trees'],
    'Food': ['Local Production', 'Organic', 'Food Waste', 'Urban Farming', 'Sustainable Diet'],
    'Building Transition': ['Concrete', 'Waste', 'Costs', 'Rent', 'Existing Stock', 'Community', 'Quality Of Life', 'Displacement', 'Wood'],
    'Heating Transition': ['Openness to Technology', 'Economically Unviable', 'Rent Increase', 'Costs', 'Monument Protection', 'District Heating', 'Old Building', 'Homeownership']
}

@app.route('/step2', methods=['POST'])
def step2_post():
    session['topics'] = request.form.getlist('topics')
    session['subtopics'] = request.form.getlist('subtopics')
    session['notes'] = request.form.get('notes', '')
    session['district'] = request.form.get('district', '')
    return redirect(url_for('step3'))

# Initiative data with details
INITIATIVES_DATA = {
    'Mitte': {
        'Urban Garden': {
            'Prinzessinnengarten': {
                'contact': 'info@prinzessinnengarten.net, +49 30 12345678',
                'summary': 'Community garden promoting urban agriculture and sustainability. Offers workshops on organic gardening and environmental education.'
            },
            'Gemeinschaftsgarten Wedding': {
                'contact': 'wedding@gemeinschaftsgarten.de, +49 30 87654321',
                'summary': 'Neighborhood garden fostering community connections through shared gardening. Focuses on local food production and social integration.'
            }
        },
        'Repair Café': {
            'Repair Café Mitte': {
                'contact': 'mitte@repaircafe-berlin.de, +49 30 11111111',
                'summary': 'Free repair service for electronics and household items. Promotes circular economy and waste reduction through community repair events.'
            },
            'Fixpunkt Reparaturcafé': {
                'contact': 'fixpunkt@repair.de, +49 30 22222222',
                'summary': 'Weekly repair meetings for bicycles and small appliances. Teaches repair skills and extends product lifecycles.'
            }
        },
        'Climate Education': {
            'Klimawerkstatt Berlin': {
                'contact': 'info@klimawerkstatt.berlin, +49 30 33333333',
                'summary': 'Educational workshops on climate change and sustainability. Provides practical tools for climate action in daily life.'
            },
            'BUND Umweltbildung': {
                'contact': 'bildung@bund-berlin.de, +49 30 44444444',
                'summary': 'Environmental education programs for all ages. Focuses on biodiversity protection and sustainable living practices.'
            }
        },
        'Policy Advocacy': {
            'Klimaneustart Berlin': {
                'contact': 'info@klimaneustart.de, +49 30 55555555',
                'summary': 'Climate policy advocacy and citizen engagement platform. Works on systemic change for Berlin\'s climate neutrality goals.'
            },
            'Changing Cities': {
                'contact': 'hello@changing-cities.org, +49 30 66666666',
                'summary': 'Urban mobility transformation advocacy group. Campaigns for car-free city centers and sustainable transport solutions.'
            }
        },
        'Mutual Aid': {
            'Kiezküche Mitte': {
                'contact': 'mitte@kiezkueche.org, +49 30 77777777',
                'summary': 'Community kitchen providing free meals and food sharing. Builds neighborhood solidarity and reduces food waste.'
            },
            'Nachbarschaftshilfe Wedding': {
                'contact': 'wedding@nachbarschaft.de, +49 30 88888888',
                'summary': 'Neighborhood support network for elderly and vulnerable residents. Organizes mutual aid and community care activities.'
            }
        },
        'Digital Inclusion': {
            'Digital für Alle': {
                'contact': 'info@digital-fuer-alle.de, +49 30 99999999',
                'summary': 'Digital literacy programs for seniors and marginalized communities. Provides free computer training and internet access.'
            },
            'Senior Internet Initiative': {
                'contact': 'senior@internet-initiative.de, +49 30 10101010',
                'summary': 'Technology education specifically designed for older adults. Offers patient, age-appropriate digital skills training.'
            }
        }
    }
}

# Add other districts with proper data structure
INITIATIVES_DATA['Neukölln'] = {
    'Urban Garden': {
        'Tempelhofer Feld Gärten': {
            'contact': 'tempelhof@garden.de, +49 30 12345678',
            'summary': 'Community garden at Tempelhof Field promoting urban agriculture. Offers workshops and community events for Neukölln residents.'
        },
        'Nachbarschaftsgarten Rixdorf': {
            'contact': 'rixdorf@garden.de, +49 30 87654321',
            'summary': 'Neighborhood garden in Rixdorf creating shared growing spaces. Focuses on environmental education and local food production.'
        }
    },
    'Repair Café': {
        'Repair Café Neukölln': {
            'contact': 'neukoelln@repaircafe.de, +49 30 11111111',
            'summary': 'Community repair service in Neukölln for electronics and household items. Promotes sustainability through repair and reuse.'
        },
        'Werkstatt der Kulturen': {
            'contact': 'kulturen@repair.de, +49 30 22222222',
            'summary': 'Multicultural repair workshop teaching practical skills. Extends product lifecycles and builds community connections across cultures.'
        }
    },
    'Climate Education': {
        'Umweltbildung Neukölln': {
            'contact': 'umwelt@neukoelln.de, +49 30 33333333',
            'summary': 'Environmental education center in Neukölln offering workshops. Empowers residents with knowledge for climate action.'
        },
        'Grüne Liga Berlin': {
            'contact': 'info@grueneliga.de, +49 30 44444444',
            'summary': 'Environmental advocacy organization with Neukölln programs. Focuses on practical sustainability and ecological awareness.'
        }
    },
    'Policy Advocacy': {
        'Bürgerinitiative Tempelhof': {
            'contact': 'tempelhof@buerger.de, +49 30 55555555',
            'summary': 'Citizen initiative for Tempelhof area climate policies. Works on neighborhood-level climate initiatives and policy change.'
        },
        'Verkehrswende Neukölln': {
            'contact': 'verkehr@neukoelln.de, +49 30 66666666',
            'summary': 'Transport transformation advocacy in Neukölln. Promotes sustainable mobility and car-free neighborhoods.'
        }
    },
    'Mutual Aid': {
        'Kiezküche Neukölln': {
            'contact': 'kueche@neukoelln.de, +49 30 77777777',
            'summary': 'Community kitchen in Neukölln providing free meals. Organizes food sharing and neighborhood support activities.'
        },
        'Solidarische Nachbarschaft': {
            'contact': 'solidarisch@neukoelln.de, +49 30 88888888',
            'summary': 'Solidarity network supporting vulnerable Neukölln residents. Provides practical support and builds social connections.'
        }
    },
    'Digital Inclusion': {
        'Digitale Nachbarschaft': {
            'contact': 'digital@nachbarschaft.de, +49 30 99999999',
            'summary': 'Digital literacy center in Neukölln offering free training. Bridges the digital divide for all community members.'
        },
        'Computer für Alle': {
            'contact': 'computer@alle.de, +49 30 10101010',
            'summary': 'Computer education program for all ages in Neukölln. Provides accessible digital skills training and support.'
        }
    }
}

# Add simplified data for remaining districts
for district in ['Kreuzberg', 'Prenzlauer Berg', 'Charlottenburg', 'Friedrichshain', 'Schöneberg', 'Wedding', 'Tempelhof', 'Steglitz']:
    INITIATIVES_DATA[district] = {
        'Urban Garden': {
            f'{district} Community Garden': {
                'contact': f'{district.lower().replace(" ", "")}@garden.de, +49 30 12345678',
                'summary': f'Local community garden in {district} promoting sustainable urban agriculture. Offers workshops and community events.'
            },
            f'{district} Green Space': {
                'contact': f'green@{district.lower().replace(" ", "")}.de, +49 30 87654321',
                'summary': f'Neighborhood green initiative in {district} creating shared growing spaces. Focuses on environmental education.'
            }
        },
        'Repair Café': {
            f'Repair Café {district}': {
                'contact': f'{district.lower().replace(" ", "")}@repaircafe.de, +49 30 11111111',
                'summary': f'Community repair service in {district} for electronics and household items. Promotes sustainability through repair.'
            },
            f'{district} Fix Workshop': {
                'contact': f'fix@{district.lower().replace(" ", "")}.de, +49 30 22222222',
                'summary': f'Weekly repair meetings in {district} teaching practical skills. Extends product lifecycles and builds community.'
            }
        },
        'Climate Education': {
            f'{district} Climate Hub': {
                'contact': f'climate@{district.lower().replace(" ", "")}.de, +49 30 33333333',
                'summary': f'Climate education center in {district} offering workshops and resources. Empowers residents with climate knowledge.'
            },
            f'Eco Education {district}': {
                'contact': f'eco@{district.lower().replace(" ", "")}.de, +49 30 44444444',
                'summary': f'Environmental education programs for {district} residents. Focuses on practical sustainability and awareness.'
            }
        },
        'Policy Advocacy': {
            f'{district} Climate Action': {
                'contact': f'action@{district.lower().replace(" ", "")}.de, +49 30 55555555',
                'summary': f'Local climate policy advocacy group in {district}. Works on neighborhood-level climate initiatives.'
            },
            f'Citizens for {district}': {
                'contact': f'citizens@{district.lower().replace(" ", "")}.de, +49 30 66666666',
                'summary': f'Citizen advocacy group in {district} promoting sustainable development. Engages in local politics.'
            }
        },
        'Mutual Aid': {
            f'{district} Solidarity': {
                'contact': f'solidarity@{district.lower().replace(" ", "")}.de, +49 30 77777777',
                'summary': f'Mutual aid network in {district} supporting community members. Organizes food sharing and support activities.'
            },
            f'Community Care {district}': {
                'contact': f'care@{district.lower().replace(" ", "")}.de, +49 30 88888888',
                'summary': f'Community care initiative in {district} for vulnerable residents. Provides practical support and connections.'
            }
        },
        'Digital Inclusion': {
            f'{district} Digital Hub': {
                'contact': f'digital@{district.lower().replace(" ", "")}.de, +49 30 99999999',
                'summary': f'Digital literacy center in {district} offering free computer training. Bridges the digital divide.'
            },
            f'Tech for All {district}': {
                'contact': f'tech@{district.lower().replace(" ", "")}.de, +49 30 10101010',
                'summary': f'Technology education program in {district} for all ages. Provides accessible digital skills training.'
            }
        }
    }

@app.route('/step3')
def step3():
    district = session.get('district', '')
    return render_template('step3.html', district=district, initiatives_data=INITIATIVES_DATA)

@app.route('/contact_info')
def contact_info():
    selected_initiatives = session.get('selected_initiatives', [])
    initiative_types = session.get('initiative_types', [])
    district = session.get('district', '')
    
    # Fallback: If no specific initiatives selected, use first initiative from each type
    if not selected_initiatives and initiative_types and district in INITIATIVES_DATA:
        selected_initiatives = []
        for init_type in initiative_types:
            if init_type in INITIATIVES_DATA[district]:
                # Get first initiative from this type
                first_initiative = list(INITIATIVES_DATA[district][init_type].keys())[0]
                selected_initiatives.append(first_initiative)
    
    # Store contact info in database for QR access (with error handling)
    try:
        contact_id = ContactShareService.create_contact_share(district, selected_initiatives)
    except Exception as e:
        print(f"Database error: {e}")
        # Generate a temporary ID for QR code
        contact_id = f"temp_{district}_{len(selected_initiatives)}"
    
    # Get detailed initiative info for display on page
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
    
    # Generate QR code with URL to public contact page
    host = request.host
    if 'localhost' in host or '127.0.0.1' in host:
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            network_ip = s.getsockname()[0]
            s.close()
            qr_url = f"http://{network_ip}:5000/public_contact/{str(contact_id)}"
        except:
            qr_url = f"http://{host}/public_contact/{str(contact_id)}"
    else:
        qr_url = f"http://{host}/public_contact/{str(contact_id)}"
    
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

@app.route('/public_contact/<contact_id>')
def public_contact(contact_id):
    # Get contact info from database
    try:
        contact_share = ContactShareService.get_contact_share(contact_id)
    except Exception as e:
        print(f"Database error in public_contact: {e}")
        contact_share = None
    
    if not contact_share:
        return render_template('contact_info.html', 
                             initiative_details=[],
                             district='Unknown',
                             qr_code=None,
                             error="Contact information not found or database unavailable",
                             public_view=True)
    
    selected_initiatives = contact_share.get('initiatives', [])
    district = contact_share.get('district', '')
    
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
    
    return render_template('contact_info.html', 
                         initiative_details=initiative_details,
                         district=district,
                         qr_code=None,
                         public_view=True)

@app.route('/show_qr')
def show_qr():
    return redirect(url_for('contact_info'))

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

@app.route('/generate_qr')
def generate_qr():
    initiative_types = session.get('initiative_types', [])
    selected_initiatives = session.get('selected_initiatives', [])
    district = session.get('district', '')
    
    qr_data = f"Klimaneustart Berlin - Initiativen in {district}\n"
    qr_data += f"Interessensbereiche: {', '.join(initiative_types)}\n"
    qr_data += f"Ausgewählte Initiativen: {', '.join(selected_initiatives)}\n\n"
    qr_data += "Kontakt Klimaneustart:\n"
    qr_data += "📧 info@klimaneustart.de\n"
    qr_data += "📱 WhatsApp: +49 30 12345678\n"
    qr_data += "🌐 www.klimaneustart.de"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('qr_code.html', qr_code=qr_code, 
                         initiative_types=initiative_types, 
                         selected_initiatives=selected_initiatives,
                         district=district)

@app.route('/step4')
def step4():
    return render_template('step4.html')

@app.route('/step4', methods=['POST'])
def step4_post():
    session['name'] = request.form.get('name', '')
    session['surname'] = request.form.get('surname', '')
    session['email'] = request.form.get('email', '')
    session['phone'] = request.form.get('phone', '')
    session['consent'] = request.form.get('consent', '')
    session['data_protection'] = request.form.get('data_protection', '')
    return redirect(url_for('step5'))

@app.route('/step5')
def step5():
    return render_template('step5.html')

@app.route('/step5', methods=['POST'])
def step5_post():
    session['reflection'] = request.form.get('reflection', '')
    session['num_people'] = request.form.get('num_people', '1')
    session['duration'] = request.form.get('duration', '0')
    session['family_status'] = request.form.get('family_status', '')
    return redirect(url_for('review'))

@app.route('/review')
def review():
    return render_template('review.html')

@app.route('/review', methods=['POST'])
def review_post():
    # Update session with edited values
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
    try:
        # Get admin user
        admin_user = UserService.get_or_create_admin()
        
        # Create dialogue using service layer
        dialogue_id = DialogueService.create_dialogue(session, admin_user['_id'])
        
        # Store dialogue ID for PDF download
        session.clear()
        session['last_dialogue_id'] = str(dialogue_id)
        
    except Exception as e:
        print(f"Database error in complete_dialogue: {e}")
        # Clear session anyway and continue without saving to database
        session.clear()
        session['last_dialogue_id'] = 'offline_mode'
    
    return render_template('thank_you.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        dashboard_data = DialogueService.get_dashboard_data()
    except Exception as e:
        print(f"Database error in dashboard: {e}")
        # Fallback data when database is unavailable
        dashboard_data = {
            'total_dialogues': 0,
            'total_partners': 0,
            'total_duration': 0,
            'dialogues': [],
            'district_stats': [],
            'theme_stats': [],
            'error': 'Database temporarily unavailable'
        }
    
    return render_template('dashboard.html', data=dashboard_data, dialogues=dashboard_data['dialogues'])

@app.route('/export/excel')
def export_excel():
    dialogues = Dialogue.find()
    
    data = []
    for d in dialogues:
        data.append({
            'ID': str(d['_id']),
            'Timestamp': d['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'Notes': d.get('notes', ''),
            'Observer Reflection': d.get('observer_reflection', ''),
            'Num People': d.get('num_people', 0),
            'Duration': d.get('duration', 0),
            'Anonymous': d.get('is_anonymous', True),
            'Consent Share Contact': d.get('consent_share_contact', False)
        })
    
    df = pd.DataFrame(data)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        df.to_excel(tmp.name, index=False, engine='openpyxl')
        tmp.seek(0)
        
        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=f'berliner_gespraeche_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

@app.route('/export/csv')
def export_csv():
    dialogues = Dialogue.find()
    
    data = []
    for d in dialogues:
        # Get embedded data
        districts = d.get('districts', [])
        interest_areas = d.get('interest_areas', [])
        topics = d.get('topics', [])
        subtopics = d.get('subtopics', [])
        contact_info = d.get('contact_info', {}) if d.get('consent_share_contact') else {}
        
        data.append({
            'ID': str(d['_id']),
            'Timestamp': d['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
            'Districts': ', '.join(districts),
            'Interest Areas': ', '.join(interest_areas),
            'Topics': ', '.join(topics),
            'Subtopics': ', '.join(subtopics),
            'Notes': d.get('notes', ''),
            'Observer Reflection': d.get('observer_reflection', ''),
            'Num People': d.get('num_people', 0),
            'Duration': d.get('duration', 0),
            'Anonymous': d.get('is_anonymous', True),
            'Consent Share Contact': d.get('consent_share_contact', False),
            'Name': contact_info.get('name', ''),
            'Email': contact_info.get('email', ''),
            'Phone': contact_info.get('phone', ''),
            'Family Status': contact_info.get('family_status', '')
        })
    
    df = pd.DataFrame(data)
    
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=berliner_gespraeche_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route('/download_dialogue_pdf')
def download_dialogue_pdf():
    dialogue_id = session.get('last_dialogue_id')
    if not dialogue_id:
        return redirect(url_for('index'))
    
    dialogue_data = DialogueService.get_dialogue_summary(dialogue_id)
    if not dialogue_data:
        return redirect(url_for('index'))
    
    dialogue = dialogue_data['dialogue']
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30)
    story.append(Paragraph("Sag doch mal, Berlin - Dialog Zusammenfassung", title_style))
    story.append(Spacer(1, 12))
    
    # Dialogue details
    story.append(Paragraph(f"<b>Datum:</b> {dialogue['created_at'].strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    districts_text = ', '.join(dialogue_data['districts']) if dialogue_data['districts'] else 'Nicht angegeben'
    story.append(Paragraph(f"<b>Bezirk:</b> {districts_text}", styles['Normal']))
    
    # Get family status from contact info if available
    if dialogue_data['contact_info'] and dialogue_data['contact_info'].get('family_status'):
        family_text = 'Alleinstehend' if dialogue_data['contact_info']['family_status'] == 'single' else 'Mit Familie'
        story.append(Paragraph(f"<b>Familienstatus:</b> {family_text}", styles['Normal']))
    
    story.append(Paragraph(f"<b>Anzahl Personen:</b> {dialogue.get('num_people', 0)}", styles['Normal']))
    story.append(Paragraph(f"<b>Dauer:</b> {dialogue.get('duration', 0)} Minuten", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Step 1
    story.append(Paragraph("<b>1. Lebenswerte Stadt:</b>", styles['Heading2']))
    story.append(Paragraph(dialogue.get('livable_city', 'Keine Angabe'), styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Dialogpartner Interesse:</b>", styles['Heading2']))
    story.append(Paragraph(dialogue.get('partner_interest', 'Keine Angabe'), styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Step 2 - Topics
    story.append(Paragraph("<b>2. Diskutierte Themen:</b>", styles['Heading2']))
    topics_text = ', '.join(dialogue_data['topics']) if dialogue_data['topics'] else 'Keine Themen ausgewählt'
    story.append(Paragraph(topics_text, styles['Normal']))
    if dialogue_data['subtopics']:
        subtopics_text = ', '.join(dialogue_data['subtopics'])
        story.append(Paragraph(f"<b>Unterthemen:</b> {subtopics_text}", styles['Normal']))
    if dialogue.get('notes'):
        story.append(Paragraph(f"<b>Notizen:</b> {dialogue['notes']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Step 3 - Interest Areas
    story.append(Paragraph("<b>3. Interessensbereiche:</b>", styles['Heading2']))
    interest_areas_text = ', '.join(dialogue_data['interest_areas']) if dialogue_data['interest_areas'] else 'Keine Bereiche ausgewählt'
    story.append(Paragraph(interest_areas_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Step 5 - Reflection
    if dialogue.get('observer_reflection'):
        story.append(Paragraph("<b>4. Reflexion:</b>", styles['Heading2']))
        story.append(Paragraph(dialogue['observer_reflection'], styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Contact info (if consent given)
    if dialogue.get('consent_share_contact') and dialogue_data['contact_info']:
        story.append(Paragraph("<b>Kontaktdaten:</b>", styles['Heading2']))
        contact = dialogue_data['contact_info']
        if contact.get('name'):
            story.append(Paragraph(f"Name: {contact['name']}", styles['Normal']))
        if contact.get('email'):
            story.append(Paragraph(f"Email: {contact['email']}", styles['Normal']))
        if contact.get('phone'):
            story.append(Paragraph(f"Telefon: {contact['phone']}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        io.BytesIO(buffer.read()),
        as_attachment=True,
        download_name=f'dialog_{dialogue["_id"]}_{dialogue["created_at"].strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )

# Initialize MongoDB on startup
try:
    from mongo_setup import setup_database
    setup_database()
except Exception as e:
    print(f"MongoDB setup warning: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    if debug:
        print("\n" + "="*50)
        print("MongoDB Berliner Gespräche Server starting...")
        print("Database: MongoDB (berliner_gespraeche)")
        print("For mobile access, use your network IP:")
        
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            network_ip = s.getsockname()[0]
            s.close()
            print(f"   http://{network_ip}:{port}")
        except:
            print("   Network IP detection failed")
        
        print(f"For local access: http://localhost:{port}")
        print("="*50 + "\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port)