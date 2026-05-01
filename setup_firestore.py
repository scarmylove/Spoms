"""
Setup script to initialize Firestore with default data
Run this once before first use: python setup_firestore.py
"""
import os
import json
import hashlib
from firebase_admin import credentials, firestore
import firebase_admin

def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def initialize_firestore():
    """Initialize Firestore with default data"""
    
    # Initialize Firebase
    if not firebase_admin._apps:
        firebase_key = os.environ.get('FIREBASE_KEY')
        if firebase_key:
            cred = credentials.Certificate(json.loads(firebase_key))
        else:
            cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # Default users
    default_users = [
        {
            'user_id': 'U001',
            'name': 'Dennis Lopez Jr',
            'username': 'dennis',
            'password': '0e66633604475ead7445c5e5f987d6450c23687eccf37665e3924541a7f8f6b3',
            'role': 'Administrator',
            'email': 'dennis@spoms.com',
            'status': 'Active',
            'profile_picture': 'images/profile-U001-1777612098.jpeg'
        },
        {
            'user_id': 'U002',
            'name': 'Jani',
            'username': 'jani',
            'password': 'dd8a3af07bf0ed457e80ebfa07a8d2a7d834bb30aaee2cbf97d3b6120e6238b8',
            'role': 'Purchasing Officer',
            'email': 'jani@spoms.com',
            'status': 'Active',
            'profile_picture': 'images/profile-U002-1777612152.jpeg'
        },
        {
            'user_id': 'U003',
            'name': 'Angel Rose Cepe',
            'username': 'angel',
            'password': '519ba91a5a5b4afb9dc66f8805ce8c442b6576316c19c6896af2fa9bda6aff71',
            'role': 'Finance Officer',
            'email': 'angel@spoms.com',
            'status': 'Active',
            'profile_picture': 'images/profile-U003-1777612183.jpg'
        },
        {
            'user_id': 'U004',
            'name': 'Jennifer Urboda',
            'username': 'jennifer',
            'password': '9ce8db922a8f4a7abd859adee70bd8b7a63321265487da54cf4bed6a69eb3e1b',
            'role': 'Store Owner',
            'email': 'jennifer@spoms.com',
            'status': 'Active',
            'profile_picture': 'images/profile-U004-1777612243.jpeg'
        }
    ]
    
    # Add default users
    print("Adding default users...")
    for user in default_users:
        db.collection('users').document(user['user_id']).set(user)
        print(f"  ✓ Created user: {user['name']} ({user['username']})")
    
    # Default settings
    default_settings = {
        'system_name': 'SPOMS',
        'logo': 'images/logo.png',
        'homepage_background': 'images/spoms.png'
    }
    
    print("Adding default settings...")
    db.collection('settings').document('config').set(default_settings)
    print("  ✓ Settings initialized")
    
    # Empty collections
    empty_collections = ['suppliers', 'orders', 'payments', 'feedback']
    print("Initializing empty collections...")
    for collection in empty_collections:
        # Just ensure they exist by checking
        docs = db.collection(collection).stream()
        print(f"  ✓ Collection '{collection}' ready")
    
    print("\n✅ Firestore initialization complete!")
    print("\nDefault login credentials:")
    print("  Username: dennis   | Role: Administrator")
    print("  Username: jani     | Role: Purchasing Officer")
    print("  Username: angel    | Role: Finance Officer")
    print("  Username: jennifer | Role: Store Owner")

if __name__ == '__main__':
    initialize_firestore()
