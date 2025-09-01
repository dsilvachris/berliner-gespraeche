# MongoDB Migration Guide

## Overview
The Berliner Gespräche application has been successfully migrated from SQLite to MongoDB.

## Changes Made

### 1. Dependencies
- **Removed**: `Flask-SQLAlchemy`
- **Added**: `pymongo`

### 2. New Files Created
- `mongo_config.py` - MongoDB connection configuration
- `mongo_models.py` - Document-based models replacing SQLAlchemy models
- `mongo_services.py` - Service layer for MongoDB operations
- `mongo_setup.py` - Database initialization script

### 3. Files Modified
- `requirements.txt` - Updated dependencies
- `app.py` - Complete rewrite for MongoDB (backup: `app_sqlite_backup.py`)
- `database_setup.py` - Updated to use MongoDB setup

### 4. Database Structure Changes

#### SQLite (Before)
- Relational tables with foreign keys
- Separate tables for relationships
- Fixed schema structure

#### MongoDB (After)
- Document-based collections
- Embedded documents for relationships
- Flexible schema structure

### 5. Key Collections

```javascript
// Users Collection
{
  _id: ObjectId,
  username: "admin",
  role: "admin",
  created_at: ISODate
}

// Dialogues Collection
{
  _id: ObjectId,
  user_id: ObjectId,
  livable_city: "string",
  partner_interest: "string",
  notes: "string",
  observer_reflection: "string",
  num_people: 1,
  duration: 30,
  is_anonymous: true,
  consent_share_contact: false,
  
  // Embedded arrays (replacing foreign key relationships)
  districts: ["Mitte"],
  topics: ["Wohnen/Bauwende"],
  subtopics: ["Affordability"],
  interest_areas: ["Urban Garden"],
  initiative_types: ["Urban Garden"],
  selected_initiatives: ["Prinzessinnengarten"],
  
  // Embedded contact info (if consent given)
  contact_info: {
    name: "John Doe",
    email: "john@example.com",
    phone: "+49 30 12345678",
    family_status: "single"
  },
  
  created_at: ISODate
}

// Contact Shares Collection (for QR codes)
{
  _id: ObjectId,
  district: "Mitte",
  initiatives: ["Prinzessinnengarten"],
  timestamp: ISODate,
  created_at: ISODate
}

// Themes Collection
{
  _id: "urban_garden",
  name: "Urban Garden",
  description: "Community gardening initiatives",
  created_at: ISODate
}
```

## Installation & Setup

### 1. Install MongoDB
```bash
# Windows (using Chocolatey)
choco install mongodb

# Or download from: https://www.mongodb.com/try/download/community
```

### 2. Start MongoDB Service
```bash
# Windows
net start MongoDB

# Or start manually
mongod --dbpath "C:\data\db"
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
python database_setup.py
```

### 5. Run Application
```bash
python app.py
```

## Benefits of MongoDB Migration

### 1. **Flexible Schema**
- No need for database migrations when adding new fields
- Easy to store complex nested data structures

### 2. **Better Performance**
- Single document queries instead of multiple JOINs
- Embedded documents reduce query complexity

### 3. **Scalability**
- Horizontal scaling capabilities
- Better handling of large datasets

### 4. **Document Structure**
- Natural fit for dialogue data with varying structures
- Easier to work with JSON-like data

### 5. **Development Speed**
- Faster prototyping and feature development
- Less boilerplate code for database operations

## Configuration

### Environment Variables
```bash
# Optional - defaults provided
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=berliner_gespraeche
```

### Connection Settings
- **Default URI**: `mongodb://localhost:27017/`
- **Database Name**: `berliner_gespraeche`
- **Collections**: `users`, `themes`, `initiatives`, `dialogues`, `contact_shares`

## Troubleshooting

### MongoDB Not Running
```bash
# Check if MongoDB is running
tasklist /FI "IMAGENAME eq mongod.exe"

# Start MongoDB service
net start MongoDB
```

### Connection Issues
- Ensure MongoDB is running on port 27017
- Check firewall settings
- Verify MongoDB installation

### Data Migration
If you have existing SQLite data, you'll need to create a migration script to transfer data from SQLite to MongoDB format.

## Rollback Plan
If needed, you can rollback to SQLite:
1. Restore `app_sqlite_backup.py` to `app.py`
2. Update `requirements.txt` to use `Flask-SQLAlchemy`
3. Run the original database setup

## Next Steps
1. Test all application features
2. Create data backup procedures
3. Set up MongoDB monitoring
4. Consider MongoDB Atlas for production deployment