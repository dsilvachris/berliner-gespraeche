# Berliner Gespräche - Streamlit Version

Ein Streamlit-basiertes Tool zur Dokumentation von Gesprächen zwischen Bürgern und Facilitatoren über die Verbesserung der Lebensqualität in Berlin.

## Deployment auf Streamlit Cloud

1. **Repository erstellen**: Lade alle Dateien in ein GitHub Repository hoch
2. **Streamlit Cloud**: Gehe zu [share.streamlit.io](https://share.streamlit.io)
3. **App deployen**: Verbinde dein GitHub Repository
4. **Hauptdatei**: Stelle sicher, dass `streamlit_app.py` als Hauptdatei erkannt wird

## Lokale Ausführung

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Wichtige Dateien für Deployment

- `streamlit_app.py` - Haupt-Streamlit-Anwendung
- `requirements.txt` - Python-Abhängigkeiten
- `README.md` - Diese Datei

## Features

- 5-Schritt Dialog-Prozess
- QR-Code Generation
- Dashboard mit Statistiken
- CSV Export
- SQLite Datenbank
- Responsive Design