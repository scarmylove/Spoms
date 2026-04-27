"""
Database initialization script - Run this once to migrate from JSON to MongoDB
or to set up default data for fresh deployment
"""

import json
import os
from datetime import datetime
import hashlib
from database import (
    get_db, 
    find_document, 
    save_document,
    load_collection
)


def hash_pwd(pwd):
    """Hash password using SHA256"""
    return hashlib.sha256(pwd.encode()).hexdigest()


def init_users():
    """Initialize users collection with default accounts"""
    db = get_db()
    
    # Check if users already exist
    if db['users'].count_documents({}) > 0:
        print("Users already exist. Skipping initialization.")
        return
    
    default_users = [
        {
            'name': 'Dennis Lopez Jr',
            'username': 'dennis',
            'password': hash_pwd('lopez'),
            'role': 'Administrator',
            'email': 'dennis@spoms.com'
        },
        {
            'name': 'Jani',
            'username': 'jani',
            'password': hash_pwd('jani'),
            'role': 'Purchasing Officer',
            'email': 'jani@spoms.com'
        },
        {
            'name': 'Angel Rose Cepe',
            'username': 'angel',
            'password': hash_pwd('angel'),
            'role': 'Finance Officer',
            'email': 'angel@spoms.com'
        },
        {
            'name': 'Jennifer Urboda',
            'username': 'jennifer',
            'password': hash_pwd('jennifer'),
            'role': 'Store Owner',
            'email': 'jennifer@spoms.com'
        }
    ]
    
    try:
        db['users'].insert_many(default_users)
        print(f"✓ Initialized {len(default_users)} users")
    except Exception as e:
        print(f"✗ Error initializing users: {e}")


def init_settings():
    """Initialize settings collection"""
    db = get_db()
    
    if db['settings'].count_documents({}) > 0:
        print("Settings already exist. Skipping initialization.")
        return
    
    default_settings = {
        'system_name': 'SPOMS',
        'logo': 'images/spoms.png',
        'homepage_background': 'images/spoms.png',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    try:
        db['settings'].insert_one(default_settings)
        print("✓ Initialized settings")
    except Exception as e:
        print(f"✗ Error initializing settings: {e}")


def migrate_json_to_mongodb():
    """Migrate existing JSON files to MongoDB"""
    data_dir = 'data'
    collections_map = {
        'users.json': 'users',
        'suppliers.json': 'suppliers',
        'orders.json': 'orders',
        'payments.json': 'payments',
        'feedback.json': 'feedback',
        'settings.json': 'settings'
    }
    
    db = get_db()
    
    for json_file, collection_name in collections_map.items():
        filepath = os.path.join(data_dir, json_file)
        
        if not os.path.exists(filepath):
            print(f"⊘ {json_file} not found, skipping...")
            continue
        
        # Skip if collection already has data
        if db[collection_name].count_documents({}) > 0:
            print(f"✓ {collection_name} already has data, skipping...")
            continue
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if not data:
                print(f"⊘ {json_file} is empty")
                continue
            
            # Ensure data is a list
            if not isinstance(data, list):
                data = [data]
            
            # Hash passwords for users collection
            if collection_name == 'users':
                for user in data:
                    if 'password' in user and len(user['password']) != 64:
                        user['password'] = hash_pwd(user['password'])
            
            db[collection_name].insert_many(data)
            print(f"✓ Migrated {len(data)} records to {collection_name}")
        
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing {json_file}: {e}")
        except Exception as e:
            print(f"✗ Error migrating {json_file}: {e}")


def initialize_database():
    """Run all initialization steps"""
    print("\n" + "="*50)
    print("🔧 Initializing SPOMS Database")
    print("="*50 + "\n")
    
    try:
        # First try to migrate existing JSON files
        migrate_json_to_mongodb()
        
        # Then initialize any missing collections
        init_users()
        init_settings()
        
        print("\n" + "="*50)
        print("✓ Database initialization completed successfully!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n✗ Fatal error during initialization: {e}")
        raise


if __name__ == '__main__':
    initialize_database()
