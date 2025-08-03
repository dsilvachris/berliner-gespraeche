from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
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

app = Flask(__name__)
app.secret_key = 'berliner_gespraeche_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///berliner_gespraeche.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Dialogue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    livable_city = db.Column(db.Text)
    partner_interest = db.Column(db.Text)
    topics = db.Column(db.JSON)
    subtopics = db.Column(db.JSON)
    notes = db.Column(db.String(100))
    district = db.Column(db.String(50))
    initiatives = db.Column(db.JSON)
    reflection = db.Column(db.Text)
    num_people = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    family_status = db.Column(db.String(50))
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    consent = db.Column(db.String(10))
    data_protection = db.Column(db.String(20))

class ContactShare(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    district = db.Column(db.String(50))
    initiatives = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start_dialogue():
    session.clear()
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
for district in ['Kreuzberg', 'Prenzlauer Berg', 'Charlottenburg']:
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
    
    # Store contact info in database for QR access
    contact_id = f"{district}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    contact_share = ContactShare(
        id=contact_id,
        district=district,
        initiatives=selected_initiatives
    )
    db.session.add(contact_share)
    db.session.commit()
    
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
    # Use request host to make it accessible from mobile devices
    host = request.host
    if 'localhost' in host or '127.0.0.1' in host:
        # Try to get network IP for mobile access
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            network_ip = s.getsockname()[0]
            s.close()
            qr_url = f"http://{network_ip}:5000/public_contact/{contact_id}"
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

@app.route('/public_contact/<contact_id>')
def public_contact(contact_id):
    # Get contact info from database
    contact_share = ContactShare.query.get(contact_id)
    
    if not contact_share:
        return render_template('contact_info.html', 
                             initiative_details=[],
                             district='Unknown',
                             qr_code=None,
                             error="Contact information not found",
                             public_view=True)
    
    selected_initiatives = contact_share.initiatives or []
    district = contact_share.district or ''
    
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
    session['initiative_types'] = request.form.getlist('initiative_types')
    session['selected_initiatives'] = request.form.getlist('selected_initiatives')
    
    # Debug: Print what was submitted
    print(f"Initiative types: {session.get('initiative_types', [])}")
    print(f"Selected initiatives: {session.get('selected_initiatives', [])}")
    print(f"All form data: {dict(request.form)}")
    
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

@app.route('/complete', methods=['POST'])
def complete_dialogue():
    # Save dialogue to database - use district from step5 if provided, otherwise from step2
    step5_district = request.form.get('district', '')
    final_district = step5_district if step5_district else session.get('district', '')
    
    dialogue = Dialogue(
        livable_city=session.get('livable_city', ''),
        partner_interest=session.get('partner_interest', ''),
        topics=session.get('topics', []),
        subtopics=session.get('subtopics', []),
        notes=session.get('notes', ''),
        district=final_district,
        initiatives=session.get('selected_initiatives', []),
        reflection=request.form.get('reflection', ''),
        num_people=int(request.form.get('num_people', 1)),
        duration=int(request.form.get('duration', 0)),
        family_status=request.form.get('family_status', ''),
        name=session.get('name', ''),
        surname=session.get('surname', ''),
        email=session.get('email', ''),
        phone=session.get('phone', ''),
        consent=session.get('consent', ''),
        data_protection=session.get('data_protection', '')
    )
    
    db.session.add(dialogue)
    db.session.commit()
    
    # Store dialogue ID for PDF download
    dialogue_id = dialogue.id
    session.clear()
    session['last_dialogue_id'] = dialogue_id
    
    return render_template('thank_you.html')

@app.route('/dashboard')
def dashboard():
    dialogues = Dialogue.query.order_by(Dialogue.timestamp.desc()).all()
    
    # Calculate dashboard data
    total_partners = sum(d.num_people for d in dialogues)
    total_duration = sum(d.duration for d in dialogues)
    
    topics = {}
    districts = {}
    
    for dialogue in dialogues:
        if dialogue.topics:
            for topic in dialogue.topics:
                topics[topic] = topics.get(topic, 0) + 1
        if dialogue.district:
            districts[dialogue.district] = districts.get(dialogue.district, 0) + 1
    
    dashboard_data = {
        'total_partners': total_partners,
        'total_duration': total_duration,
        'topics': topics,
        'districts': districts
    }
    
    return render_template('dashboard.html', data=dashboard_data, dialogues=dialogues)

@app.route('/export/excel')
def export_excel():
    dialogues = Dialogue.query.order_by(Dialogue.timestamp.desc()).all()
    
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
    dialogues = Dialogue.query.order_by(Dialogue.timestamp.desc()).all()
    
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
    
    dialogue = Dialogue.query.get_or_404(dialogue_id)
    
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
    story.append(Paragraph(f"<b>Datum:</b> {dialogue.timestamp.strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    story.append(Paragraph(f"<b>Bezirk:</b> {dialogue.district or 'Nicht angegeben'}", styles['Normal']))
    if dialogue.family_status:
        family_text = 'Alleinstehend' if dialogue.family_status == 'single' else 'Mit Familie'
        story.append(Paragraph(f"<b>Familienstatus:</b> {family_text}", styles['Normal']))
    story.append(Paragraph(f"<b>Anzahl Personen:</b> {dialogue.num_people}", styles['Normal']))
    story.append(Paragraph(f"<b>Dauer:</b> {dialogue.duration} Minuten", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Step 1
    story.append(Paragraph("<b>1. Lebenswerte Stadt:</b>", styles['Heading2']))
    story.append(Paragraph(dialogue.livable_city or 'Keine Angabe', styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Dialogpartner Interesse:</b>", styles['Heading2']))
    story.append(Paragraph(dialogue.partner_interest or 'Keine Angabe', styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Step 2
    story.append(Paragraph("<b>2. Diskutierte Themen:</b>", styles['Heading2']))
    topics_text = ', '.join(dialogue.topics) if dialogue.topics else 'Keine Themen ausgewählt'
    story.append(Paragraph(topics_text, styles['Normal']))
    if dialogue.subtopics:
        subtopics_text = ', '.join(dialogue.subtopics)
        story.append(Paragraph(f"<b>Unterthemen:</b> {subtopics_text}", styles['Normal']))
    if dialogue.notes:
        story.append(Paragraph(f"<b>Notizen:</b> {dialogue.notes}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Step 3
    story.append(Paragraph("<b>3. Ausgewählte Initiativen:</b>", styles['Heading2']))
    initiatives_text = ', '.join(dialogue.initiatives) if dialogue.initiatives else 'Keine Initiativen ausgewählt'
    story.append(Paragraph(initiatives_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Step 5
    if dialogue.reflection:
        story.append(Paragraph("<b>4. Reflexion:</b>", styles['Heading2']))
        story.append(Paragraph(dialogue.reflection, styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Contact info (if consent given)
    if dialogue.consent == 'yes':
        story.append(Paragraph("<b>Kontaktdaten:</b>", styles['Heading2']))
        if dialogue.name or dialogue.surname:
            name_text = f"{dialogue.name or ''} {dialogue.surname or ''}".strip()
            story.append(Paragraph(f"Name: {name_text}", styles['Normal']))
        if dialogue.email:
            story.append(Paragraph(f"Email: {dialogue.email}", styles['Normal']))
        if dialogue.phone:
            story.append(Paragraph(f"Telefon: {dialogue.phone}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        io.BytesIO(buffer.read()),
        as_attachment=True,
        download_name=f'dialog_{dialogue.id}_{dialogue.timestamp.strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("\n" + "="*50)
    print("🌐 Server starting...")
    print("📱 For mobile access, use your network IP:")
    
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        network_ip = s.getsockname()[0]
        s.close()
        print(f"   http://{network_ip}:5000")
    except:
        print("   Network IP detection failed")
    
    print("💻 For local access: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)