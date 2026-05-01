from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
import hashlib
from firebase_admin import credentials, firestore
import firebase_admin

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or 'spoms-secret-2026'

# Session configuration - using cookies instead of filesystem for Vercel
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.permanent_session_lifetime = timedelta(hours=24)

# Initialize Firebase
if not firebase_admin._apps:
    # Check if running on Vercel (FIREBASE_KEY env var) or locally (firebase-key.json)
    firebase_key = os.environ.get('FIREBASE_KEY')
    if firebase_key:
        # Vercel deployment: use environment variable
        cred = credentials.Certificate(json.loads(firebase_key))
    else:
        # Local development: use firebase-key.json
        cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Ensure static/images directory exists
os.makedirs('static/images', exist_ok=True)


# ===== FIREBASE HELPER FUNCTIONS =====
def get_collection_data(collection_name):
    """Get all documents from a collection as a list"""
    try:
        docs = db.collection(collection_name).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error getting {collection_name}: {e}")
        return []


def add_to_collection(collection_name, data):
    """Add a document to a collection"""
    try:
        db.collection(collection_name).add(data)
        return True
    except Exception as e:
        print(f"Error adding to {collection_name}: {e}")
        return False


def update_collection_doc(collection_name, doc_id, data):
    """Update a specific document in a collection"""
    try:
        db.collection(collection_name).document(doc_id).update(data)
        return True
    except Exception as e:
        print(f"Error updating {collection_name}: {e}")
        return False


def delete_from_collection(collection_name, doc_id):
    """Delete a document from a collection"""
    try:
        db.collection(collection_name).document(doc_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting from {collection_name}: {e}")
        return False


def get_document(collection_name, doc_id):
    """Get a specific document from a collection"""
    try:
        doc = db.collection(collection_name).document(doc_id).get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"Error getting document from {collection_name}: {e}")
        return None


def get_settings():
    """Get system settings from Firestore"""
    try:
        doc = db.collection('settings').document('config').get()
        if doc.exists:
            return doc.to_dict()
        return default_settings()
    except Exception as e:
        print(f"Error getting settings: {e}")
        return default_settings()


def save_settings(settings):
    """Save system settings to Firestore"""
    try:
        db.collection('settings').document('config').set(settings)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


def get_current_user():
    """Get current user from session and Firestore"""
    if 'user' in session:
        try:
            users = db.collection('users').where('name', '==', session['user']).stream()
            user = next((doc.to_dict() for doc in users), None)
            return user
        except Exception as e:
            print(f"Error getting current user: {e}")
            return None
    return None


def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'svg'}


@app.context_processor
def inject_settings():
    return {'settings': get_settings()}


@app.context_processor
def inject_current_user():
    return {'current_user': get_current_user()}


def default_settings():
    return {
        'system_name': 'SPOMS',
        'logo': 'images/spoms.png',
        'homepage_background': 'images/spoms.png'
    }


# ===== DECORATORS =====
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ===== FEEDBACK PAGE =====

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/api/feedback', methods=['GET', 'POST'])
def api_feedback():
    if request.method == 'POST':
        data = request.json
        feedback_data = {
            "name": data.get('name'),
            "message": data.get('message'),
            "rating": data.get('rating'),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        if add_to_collection('feedback', feedback_data):
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Failed to save feedback"}), 500

    feedbacks = get_collection_data('feedback')
    return jsonify(feedbacks)

def role_check(roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            if session['role'] not in roles:
                return render_template('403.html'), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ===== MGA ROUTES =====
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        users = get_collection_data('users')
        u = next((x for x in users if x.get('username') == user), None)
        if u and u.get('password') == hash_pwd(pwd):
            session['user'] = u.get('name')
            session['role'] = u.get('role')
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    suppliers = get_collection_data('suppliers')
    orders = get_collection_data('orders')
    payments = get_collection_data('payments')
    
    stats = {
        'suppliers': len(suppliers),
        'orders': len(orders),
        'pending': len([o for o in orders if o.get('status') == 'Pending']),
        'completed': len([o for o in orders if o.get('status') == 'Delivered']),
        'payments': len(payments)
    }
    return render_template('dashboard.html', stats=stats, role=session['role'])

@app.route('/suppliers')
@login_required
def suppliers():
    if session['role'] not in ['Administrator', 'Purchasing Officer', 'Store Owner']:
        return render_template('403.html'), 403
    data = get_collection_data('suppliers')
    return render_template('suppliers.html', suppliers=data, role=session['role'])

@app.route('/api/suppliers', methods=['GET', 'POST'])
@login_required
def api_suppliers():
    if request.method == 'POST':
        try:
            if session.get('role') not in ['Administrator', 'Store Owner']:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            if add_to_collection('suppliers', data):
                return jsonify({'success': True})
            return jsonify({'success': False, 'error': 'Failed to save supplier'}), 500
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    suppliers = get_collection_data('suppliers')
    return jsonify(suppliers)

@app.route('/api/suppliers/<sid>', methods=['DELETE', 'PUT'])
@login_required
@role_check(['Administrator', 'Store Owner'])
def api_supplier(sid):
    if request.method == 'DELETE':
        if delete_from_collection('suppliers', sid):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to delete supplier'}), 500
    elif request.method == 'PUT':
        data = request.json
        if update_collection_doc('suppliers', sid, data):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to update supplier'}), 500

@app.route('/orders')
@login_required
def orders():
    if session['role'] not in ['Administrator', 'Purchasing Officer', 'Finance Officer']:
        return render_template('403.html'), 403
    data = get_collection_data('orders')
    suppliers = get_collection_data('suppliers')
    return render_template('purchase_orders.html', orders=data, suppliers=suppliers, role=session['role'])

@app.route('/api/orders', methods=['GET', 'POST'])
@login_required
def api_orders():
    if request.method == 'POST':
        data = request.json
        if add_to_collection('orders', data):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to create order'}), 500
    orders = get_collection_data('orders')
    return jsonify(orders)

@app.route('/api/orders/<po_number>', methods=['PUT'])
@login_required
def update_order(po_number):
    if session.get('role') not in ['Administrator', 'Purchasing Officer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    if update_collection_doc('orders', po_number, data):
        return jsonify({'success': True})
    return jsonify({'error': 'Order not found'}), 404

@app.route('/payments')
@login_required
@role_check(['Finance Officer', 'Administrator'])
def payments():
    data = get_collection_data('payments')
    orders = get_collection_data('orders')
    return render_template('payments.html', payments=data, orders=orders, user_role=session.get('role'))

@app.route('/api/payments', methods=['GET', 'POST'])
@login_required
def api_payments():
    if request.method == 'POST':
        data = request.json
        if add_to_collection('payments', data):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to create payment'}), 500
    payments = get_collection_data('payments')
    return jsonify(payments)

@app.route('/api/payments/<payment_id>', methods=['PUT'])
@login_required
def update_payment(payment_id):
    if session.get('role') not in ['Administrator', 'Finance Officer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    if update_collection_doc('payments', payment_id, data):
        return jsonify({'success': True})
    return jsonify({'error': 'Payment not found'}), 404

@app.route('/backup')
@login_required
def backup():
    suppliers = get_collection_data('suppliers')
    orders = get_collection_data('orders')
    payments = get_collection_data('payments')
    
    return render_template('backup.html', 
        suppliers_count=len(suppliers),
        orders_count=len(orders),
        orders_value=sum(o.get('total', 0) for o in orders),
        payments_count=len(payments),
        payments_total=sum(p.get('amount', 0) for p in payments)
    )

@app.route('/reports')
@login_required
def reports():
    suppliers = get_collection_data('suppliers')
    orders = get_collection_data('orders')
    payments = get_collection_data('payments')
    feedbacks = get_collection_data('feedback')
    
    return render_template('reports.html', 
        suppliers_count=len(suppliers),
        orders_count=len(orders),
        orders_value=sum(o.get('total', 0) for o in orders),
        payments_count=len(payments),
        payments_total=sum(p.get('amount', 0) for p in payments),
        orders=orders,
        feedbacks=feedbacks
    )

@app.route('/api/chart/orders')
@login_required
def chart_orders():
    orders = get_collection_data('orders')
    statuses = ['Pending', 'Approved', 'Delivered']
    data = [len([o for o in orders if o.get('status') == s]) for s in statuses]
    return jsonify({'labels': statuses, 'data': data, 'colors': ['#f59e0b', '#3b82f6', '#10b981']})

@app.route('/api/chart/suppliers')
@login_required
def chart_suppliers():
    suppliers = get_collection_data('suppliers')
    orders = get_collection_data('orders')
    labels = [s.get('name', '') for s in suppliers]
    data = [len([o for o in orders if o.get('supplier') == s.get('name')]) for s in suppliers]
    return jsonify({'labels': labels, 'data': data, 'colors': ['#2563eb', '#dc2626', '#16a34a']})

@app.route('/users')
@login_required
@role_check(['Administrator'])
def users():
    data = get_collection_data('users')
    for u in data:
        u.pop('password', None)
    return render_template('users.html', users=data)

@app.route('/api/users', methods=['GET', 'POST'])
@login_required
@role_check(['Administrator'])
def api_users():
    users_list = get_collection_data('users')
    if request.method == 'POST':
        data = request.json
        if not data.get('username') or not data.get('password') or not data.get('name') or not data.get('role'):
            return jsonify({'success': False, 'error': 'Missing user data'}), 400
        if any(u.get('username', '').lower() == data['username'].lower() for u in users_list):
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
        data['password'] = hash_pwd(data['password'])
        existing_ids = [int(u.get('user_id', 'U0')[1:]) for u in users_list if u.get('user_id', '').startswith('U') and u.get('user_id', 'U0')[1:].isdigit()]
        next_id = max(existing_ids, default=0) + 1
        data['user_id'] = f'U{next_id:02d}'
        data['status'] = data.get('status', 'Active')
        if add_to_collection('users', data):
            return jsonify({'success': True, 'user': {'user_id': data['user_id'], 'name': data['name'], 'username': data['username'], 'role': data['role'], 'status': data['status']}})
        return jsonify({'success': False, 'error': 'Failed to create user'}), 500
    
    for u in users_list:
        u.pop('password', None)
    return jsonify(users_list)

@app.route('/api/users/<uid>', methods=['PUT', 'DELETE'])
@login_required
@role_check(['Administrator'])
def api_user(uid):
    users_list = get_collection_data('users')
    user = next((u for u in users_list if u.get('user_id') == uid), None)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    if request.method == 'DELETE':
        if delete_from_collection('users', uid):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to delete user'}), 500

    data = request.json or {}
    if data.get('username') and data['username'].lower() != user.get('username', '').lower():
        if any(u.get('username', '').lower() == data['username'].lower() for u in users_list if u.get('user_id') != uid):
            return jsonify({'success': False, 'error': 'Username already exists'}), 400
    if data.get('name'):
        user['name'] = data['name']
    if data.get('username'):
        user['username'] = data['username']
    if data.get('role'):
        user['role'] = data['role']
    if data.get('status'):
        user['status'] = data['status']
    if data.get('password'):
        user['password'] = hash_pwd(data['password'])

    if update_collection_doc('users', uid, user):
        return jsonify({'success': True, 'user': {'user_id': user['user_id'], 'name': user['name'], 'username': user['username'], 'role': user['role'], 'status': user['status']}})
    return jsonify({'success': False, 'error': 'Failed to update user'}), 500

@app.route('/settings', methods=['GET', 'POST'])
@login_required
@role_check(['Administrator'])
def settings():
    settings_data = get_settings()
    message = None
    if request.method == 'POST':
        system_name = request.form.get('system_name', settings_data['system_name']).strip()
        settings_data['system_name'] = system_name or settings_data['system_name']

        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                logo_path = f'images/site-logo-{int(datetime.now().timestamp())}.{filename.rsplit(".", 1)[1].lower()}'
                logo_file.save(os.path.join('static', logo_path))
                settings_data['logo'] = logo_path

        if 'background' in request.files:
            bg_file = request.files['background']
            if bg_file and allowed_file(bg_file.filename):
                filename = secure_filename(bg_file.filename)
                bg_path = f'images/homepage-bg-{int(datetime.now().timestamp())}.{filename.rsplit(".", 1)[1].lower()}'
                bg_file.save(os.path.join('static', bg_path))
                settings_data['homepage_background'] = bg_path

        save_settings(settings_data)
        message = 'Settings saved successfully.'

    return render_template('settings.html', settings=settings_data, message=message)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    users_list = get_collection_data('users')
    user = next((u for u in users_list if u.get('name') == session['user']), None)
    if not user:
        return redirect(url_for('logout'))
    message = None
    if request.method == 'POST':
        data = request.form
        if data.get('name'):
            user['name'] = data['name'].strip()
            session['user'] = user['name']
        if data.get('username'):
            if data['username'].lower() != user.get('username', '').lower():
                if any(u.get('username', '').lower() == data['username'].lower() for u in users_list if u != user):
                    message = 'Username already exists'
                else:
                    user['username'] = data['username'].strip()
        if data.get('password'):
            user['password'] = hash_pwd(data['password'])
        
        if 'profile_picture' in request.files:
            pic_file = request.files['profile_picture']
            if pic_file and allowed_file(pic_file.filename):
                filename = secure_filename(pic_file.filename)
                pic_path = f'images/profile-{user["user_id"]}-{int(datetime.now().timestamp())}.{filename.rsplit(".", 1)[1].lower()}'
                pic_file.save(os.path.join('static', pic_path))
                user['profile_picture'] = pic_path
        
        user_id = user.get('user_id')
        if update_collection_doc('users', user_id, user):
            if not message:
                message = 'Profile updated successfully.'
        else:
            message = 'Error updating profile. Please try again.'
    return render_template('profile.html', user=user, message=message)

if __name__ == '__main__':
    app.run(debug=True)