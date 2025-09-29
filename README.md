# Sag doch mal, Berlin - Hören. Reden. Mitgestalten
## Klimaneustart Dialog Tool

Ein mobiles/web-basiertes Tool zur Dokumentation von Gesprächen zwischen Bürgern und Facilitatoren über die Verbesserung der Lebensqualität in Berlin.

## Features

- **5-Schritt Dialog-Prozess**: Von der Essenz-Erfassung bis zur Reflexion
- **QR-Code Generation**: Für Kontaktdaten und Initiative-Informationen
- **Dashboard**: Übersicht über alle geführten Dialoge und Statistiken
- **Responsive Design**: Optimiert für mobile Geräte
- **Datenschutz**: Flexible Optionen für Datenverarbeitung

## Installation

1. **Abhängigkeiten installieren**:
```bash
pip install -r requirements.txt
```

2. **PostgreSQL Setup**:
```bash
# PostgreSQL starten und Datenbank erstellen
psql -U postgres
CREATE DATABASE berliner_gespraeche;
\q

# Umgebungsvariablen kopieren (optional)
cp .env.example .env
```

3. **Anwendung starten**:
```bash
python app.py
```

4. **Browser öffnen**: http://localhost:5000

*PostgreSQL muss lokal installiert sein. Die Datenbank-Tabellen werden automatisch erstellt.*

## Verwendung

### Für Bürger/Gesprächspartner:
1. Auf "Dialog starten" klicken
2. Den 5-Schritt Prozess durchlaufen
3. QR-Code für Kontaktdaten erhalten
4. Dialog abschließen

### Für Facilitatoren/Notiz-Macher:
1. Dashboard über die Startseite aufrufen
2. Statistiken und Insights einsehen
3. Letzte Dialoge überprüfen

## Technische Details

- **Backend**: Python Flask
- **Frontend**: HTML/CSS/JavaScript
- **QR-Code**: qrcode Library
- **Datenspeicherung**: PostgreSQL Datenbank (berliner_gespraeche)

## Struktur

```
├── app.py              # Haupt-Flask-Anwendung
├── database.py         # PostgreSQL Datenbank-Setup
├── requirements.txt    # Python-Abhängigkeiten
├── .env.example        # Umgebungsvariablen-Beispiel
├── templates/          # HTML-Templates
│   ├── base.html      # Basis-Template
│   ├── index.html     # Startseite
│   ├── step1.html     # Dialog-Essenz
│   ├── step2.html     # Themen-Auswahl
│   ├── step3.html     # Initiative-Auswahl
│   ├── step4.html     # Kontakt & Einverständnis
│   ├── step5.html     # Reflexion
│   ├── qr_code.html   # QR-Code Anzeige
│   ├── thank_you.html # Danke-Seite
│   └── dashboard.html # Dashboard
└── README.md          # Diese Datei
```

## Nächste Schritte für Produktion

1. ✅ Datenbank-Integration (PostgreSQL)
2. Benutzer-Authentifizierung
3. Export-Funktionen (CSV/PDF)
4. Erweiterte Analytics
5. Mobile App (React Native/Flutter)
6. Cloud PostgreSQL Deployment
7. SSL/HTTPS Konfiguration