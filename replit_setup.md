# Hosting Berliner Gespräche on Replit

## Setup Steps:

### 1. Create New Repl
- Go to replit.com
- Click "Create Repl"
- Choose "Python" template
- Name: "berliner-gespraeche"

### 2. Upload Files
Upload these files to your Repl:
- `app.py`
- `requirements.txt`
- `database_setup.py`
- All files in `templates/` folder
- `static/` folder (if exists)

### 3. Update requirements.txt for Replit
```
Flask==2.3.3
qrcode==7.4.2
Pillow==10.0.1
Flask-SQLAlchemy==3.0.5
pandas==2.1.1
openpyxl==3.1.2
```

### 4. Create main.py (Replit entry point)
```python
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 5. Update app.py for Replit
Change the last lines in app.py:
```python
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 6. Run the Application
- Click "Run" button in Replit
- Database will be created automatically
- Website will be accessible via Replit's provided URL

## Replit Configuration:

### .replit file (create this):
```
run = "python main.py"
language = "python3"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "python main.py"]
```

### pyproject.toml (create this):
```toml
[tool.poetry]
name = "berliner-gespraeche"
version = "0.1.0"
description = "Climate dialogue documentation tool"
authors = ["Your Name"]

[tool.poetry.dependencies]
python = "^3.10"
Flask = "2.3.3"
qrcode = "7.4.2"
Pillow = "10.0.1"
Flask-SQLAlchemy = "3.0.5"
pandas = "2.1.1"
openpyxl = "3.1.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Benefits of Replit Hosting:

✅ **Free hosting**
✅ **Automatic HTTPS**
✅ **Easy deployment**
✅ **Built-in database storage**
✅ **Collaborative editing**
✅ **Always-on option (with paid plan)**

## Limitations:

⚠️ **Free tier sleeps after inactivity**
⚠️ **Limited storage space**
⚠️ **Slower than dedicated hosting**

## Alternative: Replit Deployments

For production use:
1. Use Replit's "Deploy" feature
2. Get custom domain
3. Always-on hosting
4. Better performance

The website will be fully functional on Replit with all features working including database, QR generation, and file exports.