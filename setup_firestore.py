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
            'user_id': 'U01',
            'name': 'Dennis Lopez',
            'username': 'dennis',
            'password': hash_pwd('lopez'),
            'role': 'Administrator',
            'status': 'Active'
        },
        {
            'user_id': 'U02',
            'name': 'John Lester Poquita',
            'username': 'jani',
            'password': hash_pwd('jani'),
            'role': 'Purchasing Officer',
            'status': 'Active'
        },
        {
            'user_id': 'U03',
            'name': 'Angel Rose Cepe',
            'username': 'angel',
            'password': hash_pwd('angel'),
            'role': 'Finance Officer',
            'status': 'Active'
        },
        {
            'user_id': 'U04',
            'name': 'Jennifer Urboda',
            'username': 'jennifer',
            'password': hash_pwd('jennifer'),
            'role': 'Store Owner',
            'status': 'Active'
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
    print("  Username: dennis  | Password: lopez    | Role: Administrator")
    print("  Username: jani    | Password: jani     | Role: Purchasing Officer")
    print("  Username: angel   | Password: angel    | Role: Finance Officer")
    print("  Username: jennifer| Password: jennifer | Role: Store Owner")

if __name__ == '__main__':
    initialize_firestore()
