import streamlit as st
import sqlite3
import qrcode
import io
import base64
from datetime import datetime
import json
import pandas as pd

# Page config
st.set_page_config(
    page_title="Berliner Gespräche - Klimaneustart Dialog Tool",
    page_icon="🏙️",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('berliner_gespraeche.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dialogues
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  livable_city TEXT,
                  partner_interest TEXT,
                  topics TEXT,
                  notes TEXT,
                  district TEXT,
                  initiatives TEXT,
                  reflection TEXT,
                  num_people INTEGER,
                  duration INTEGER,
                  email TEXT,
                  phone TEXT,
                  consent TEXT,
                  data_protection TEXT)''')
    conn.commit()
    conn.close()

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'dialogue_data' not in st.session_state:
    st.session_state.dialogue_data = {}

# Initiative data
INITIATIVES_DATA = {
    'Mitte': {
        'Urban Garden': ['Prinzessinnengarten', 'Gemeinschaftsgarten Wedding'],
        'Repair Café': ['Repair Café Mitte', 'Fixpunkt Reparaturcafé'],
        'Climate Education': ['Klimawerkstatt Berlin', 'BUND Umweltbildung'],
        'Policy Advocacy': ['Klimaneustart Berlin', 'Changing Cities'],
        'Mutual Aid': ['Kiezküche Mitte', 'Nachbarschaftshilfe Wedding'],
        'Digital Inclusion': ['Digital für Alle', 'Senior Internet Initiative']
    },
    'Neukölln': {
        'Urban Garden': ['Tempelhofer Feld Gärten', 'Nachbarschaftsgarten Rixdorf'],
        'Repair Café': ['Repair Café Neukölln', 'Werkstatt der Kulturen'],
        'Climate Education': ['Umweltbildung Neukölln', 'Grüne Liga Berlin'],
        'Policy Advocacy': ['Bürgerinitiative Tempelhof', 'Verkehrswende Neukölln'],
        'Mutual Aid': ['Kiezküche Neukölln', 'Solidarische Nachbarschaft'],
        'Digital Inclusion': ['Digitale Nachbarschaft', 'Computer für Alle']
    }
}

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()

def save_dialogue():
    conn = sqlite3.connect('berliner_gespraeche.db')
    c = conn.cursor()
    c.execute('''INSERT INTO dialogues 
                 (timestamp, livable_city, partner_interest, topics, notes, district, 
                  initiatives, reflection, num_people, duration, email, phone, consent, data_protection)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (datetime.now().isoformat(),
               st.session_state.dialogue_data.get('livable_city', ''),
               st.session_state.dialogue_data.get('partner_interest', ''),
               json.dumps(st.session_state.dialogue_data.get('topics', [])),
               st.session_state.dialogue_data.get('notes', ''),
               st.session_state.dialogue_data.get('district', ''),
               json.dumps(st.session_state.dialogue_data.get('initiatives', [])),
               st.session_state.dialogue_data.get('reflection', ''),
               st.session_state.dialogue_data.get('num_people', 1),
               st.session_state.dialogue_data.get('duration', 0),
               st.session_state.dialogue_data.get('email', ''),
               st.session_state.dialogue_data.get('phone', ''),
               st.session_state.dialogue_data.get('consent', ''),
               st.session_state.dialogue_data.get('data_protection', '')))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Main app
st.title("🏙️ Berliner Gespräche - Klimaneustart Dialog Tool")

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Dialog starten", "Dashboard"])

if page == "Dialog starten":
    if st.session_state.step == 0:
        st.header("Willkommen!")
        st.write("Dokumentiere Gespräche zwischen Bürgern und Facilitatoren über die Verbesserung der Lebensqualität in Berlin.")
        
        if st.button("🚀 Dialog starten"):
            st.session_state.step = 1
            st.rerun()
    
    elif st.session_state.step == 1:
        st.header("Schritt 1: Dialog-Essenz")
        
        livable_city = st.text_area("Was macht für Sie eine lebenswerte Stadt aus?")
        partner_interest = st.text_area("Wofür interessiert sich Ihr Gesprächspartner?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Zurück"):
                st.session_state.step = 0
                st.rerun()
        with col2:
            if st.button("Weiter"):
                st.session_state.dialogue_data['livable_city'] = livable_city
                st.session_state.dialogue_data['partner_interest'] = partner_interest
                st.session_state.step = 2
                st.rerun()
    
    elif st.session_state.step == 2:
        st.header("Schritt 2: Themen-Auswahl")
        
        topics = st.multiselect("Welche Themen wurden besprochen?", 
                               ["Klimaschutz", "Mobilität", "Energie", "Ernährung", 
                                "Wohnen", "Grünflächen", "Gemeinschaft", "Digitalisierung"])
        
        notes = st.text_input("Kurze Notiz (max. 100 Zeichen)", max_chars=100)
        district = st.selectbox("Bezirk", ["", "Mitte", "Neukölln", "Kreuzberg", "Prenzlauer Berg", "Charlottenburg"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Zurück"):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button("Weiter"):
                st.session_state.dialogue_data['topics'] = topics
                st.session_state.dialogue_data['notes'] = notes
                st.session_state.dialogue_data['district'] = district
                st.session_state.step = 3
                st.rerun()
    
    elif st.session_state.step == 3:
        st.header("Schritt 3: Initiative-Auswahl")
        
        district = st.session_state.dialogue_data.get('district', '')
        if district and district in INITIATIVES_DATA:
            st.write(f"Initiativen in {district}:")
            
            selected_initiatives = []
            for category, initiatives in INITIATIVES_DATA[district].items():
                st.subheader(category)
                for initiative in initiatives:
                    if st.checkbox(initiative):
                        selected_initiatives.append(initiative)
            
            if selected_initiatives:
                if st.button("QR-Code generieren"):
                    qr_data = f"Klimaneustart Berlin - Initiativen in {district}\n"
                    qr_data += f"Ausgewählte Initiativen: {', '.join(selected_initiatives)}\n\n"
                    qr_data += "Kontakt Klimaneustart:\n"
                    qr_data += "📧 info@klimaneustart.de\n"
                    qr_data += "📱 WhatsApp: +49 30 12345678\n"
                    qr_data += "🌐 www.klimaneustart.de"
                    
                    qr_code = generate_qr_code(qr_data)
                    st.image(f"data:image/png;base64,{qr_code}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Zurück"):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button("Weiter"):
                st.session_state.dialogue_data['initiatives'] = selected_initiatives if 'selected_initiatives' in locals() else []
                st.session_state.step = 4
                st.rerun()
    
    elif st.session_state.step == 4:
        st.header("Schritt 4: Kontakt & Einverständnis")
        
        email = st.text_input("E-Mail (optional)")
        phone = st.text_input("Telefon (optional)")
        consent = st.radio("Einverständnis zur Kontaktaufnahme", ["Ja", "Nein"])
        data_protection = st.radio("Datenschutz", ["Zustimmung", "Ablehnung"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Zurück"):
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button("Weiter"):
                st.session_state.dialogue_data['email'] = email
                st.session_state.dialogue_data['phone'] = phone
                st.session_state.dialogue_data['consent'] = consent
                st.session_state.dialogue_data['data_protection'] = data_protection
                st.session_state.step = 5
                st.rerun()
    
    elif st.session_state.step == 5:
        st.header("Schritt 5: Reflexion")
        
        reflection = st.text_area("Reflexion zum Gespräch")
        num_people = st.number_input("Anzahl Gesprächspartner", min_value=1, value=1)
        duration = st.number_input("Gesprächsdauer (Minuten)", min_value=0, value=0)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Zurück"):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button("Dialog abschließen"):
                st.session_state.dialogue_data['reflection'] = reflection
                st.session_state.dialogue_data['num_people'] = num_people
                st.session_state.dialogue_data['duration'] = duration
                save_dialogue()
                st.success("Dialog erfolgreich gespeichert!")
                st.balloons()
                st.session_state.step = 0
                st.session_state.dialogue_data = {}
                st.rerun()

elif page == "Dashboard":
    st.header("📊 Dashboard")
    
    conn = sqlite3.connect('berliner_gespraeche.db')
    df = pd.read_sql_query("SELECT * FROM dialogues ORDER BY timestamp DESC", conn)
    conn.close()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamt Dialoge", len(df))
        with col2:
            total_people = df['num_people'].sum()
            st.metric("Gesamt Gesprächspartner", total_people)
        with col3:
            total_duration = df['duration'].sum()
            st.metric("Gesamt Dauer (Min)", total_duration)
        
        st.subheader("Letzte Dialoge")
        st.dataframe(df[['timestamp', 'district', 'topics', 'notes']].head(10))
        
        if st.button("Als CSV exportieren"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="CSV herunterladen",
                data=csv,
                file_name=f'berliner_gespraeche_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
    else:
        st.info("Noch keine Dialoge vorhanden.")