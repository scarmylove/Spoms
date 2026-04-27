from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from werkzeug.utils import secure_filename
from config import Config
from database import (
    get_db, 
    load_collection, 
    save_document,
    find_document,
    update_document,
    delete_document
)
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import hashlib
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs('static/images', exist_ok=True)

# ===== UTILITY FUNCTIONS =====

def hash_pwd(pwd):
    """Hash password using SHA256"""
    return hashlib.sha256(pwd.encode()).hexdigest()


def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'svg'}


def default_settings():
    """Return default settings"""
    return {
        'system_name': 'SPOMS',
        'logo': 'images/spoms.png',
        'homepage_background': 'images/spoms.png'
    }


def load_settings():
    """Load settings from MongoDB"""
    try:
        db = get_db()
        settings = db['settings'].find_one({}, {'_id': 0})
        if not settings:
            settings = default_settings()
            db['settings'].insert_one(settings)
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return default_settings()


def save_settings(settings):
    """Save settings to MongoDB"""
    try:
        db = get_db()
        db['settings'].update_one({}, {'$set': settings}, upsert=True)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")


# ===== CONTEXT PROCESSORS =====

@app.context_processor
def inject_settings():
    return {'settings': load_settings()}


@app.context_processor
def inject_current_user():
    if 'user' in session:
        try:
            db = get_db()
            user = db['users'].find_one({'name': session['user']}, {'_id': 0, 'password': 0})
            return {'current_user': user}
        except Exception as e:
            logger.error(f"Error fetching current user: {e}")
            return {'current_user': None}
    return {'current_user': None}


# ===== DECORATORS =====

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def role_check(roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                return render_template('403.html'), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ===== AUTHENTICATION ROUTES =====

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            db = get_db()
            user = db['users'].find_one({'username': username}, {'_id': 0})
            
            if user and user.get('password') == hash_pwd(password):
                session['user'] = user['name']
                session['role'] = user['role']
                session.permanent = True
                app.permanent_session_lifetime = timedelta(hours=1)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid credentials')
        except Exception as e:
            logger.error(f"Login error: {e}")
            return render_template('login.html', error='An error occurred during login')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ===== DASHBOARD ROUTE =====

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        db = get_db()
        suppliers = list(db['suppliers'].find({}, {'_id': 0}))
        orders = list(db['orders'].find({}, {'_id': 0}))
        payments = list(db['payments'].find({}, {'_id': 0}))
        
        stats = {
            'suppliers': len(suppliers),
            'orders': len(orders),
            'pending': len([o for o in orders if o.get('status') == 'Pending']),
            'completed': len([o for o in orders if o.get('status') == 'Delivered']),
            'payments': len(payments)
        }
        return render_template('dashboard.html', stats=stats, role=session.get('role'))
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('dashboard.html', stats={}, role=session.get('role'))

# ===== SUPPLIERS ROUTES =====

@app.route('/suppliers')
@login_required
def suppliers():
    if session.get('role') not in ['Administrator', 'Purchasing Officer', 'Store Owner']:
        return render_template('403.html'), 403
    
    try:
        db = get_db()
        data = list(db['suppliers'].find({}, {'_id': 0}))
        return render_template('suppliers.html', suppliers=data, role=session.get('role'))
    except Exception as e:
        logger.error(f"Suppliers error: {e}")
        return render_template('suppliers.html', suppliers=[], role=session.get('role'))


@app.route('/api/suppliers', methods=['GET', 'POST'])
@login_required
def api_suppliers():
    try:
        db = get_db()
        
        if request.method == 'POST':
            if session.get('role') not in ['Administrator', 'Store Owner']:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            data = request.get_json()
            db['suppliers'].insert_one(data)
            return jsonify({'success': True})
        
        suppliers = list(db['suppliers'].find({}, {'_id': 0}))
        return jsonify(suppliers)
    except Exception as e:
        logger.error(f"API suppliers error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/suppliers/<sid>', methods=['DELETE', 'PUT'])
@login_required
@role_check(['Administrator', 'Store Owner'])
def api_supplier(sid):
    try:
        db = get_db()
        
        if request.method == 'DELETE':
            result = db['suppliers'].delete_one({'id': sid})
            return jsonify({'success': result.deleted_count > 0})
        
        elif request.method == 'PUT':
            data = request.get_json()
            result = db['suppliers'].update_one({'id': sid}, {'$set': data})
            return jsonify({'success': result.modified_count > 0})
    except Exception as e:
        logger.error(f"API supplier error: {e}")
        return jsonify({'error': str(e)}), 500

# ===== PURCHASE ORDERS ROUTES =====

@app.route('/orders')
@login_required
def orders():
    if session.get('role') not in ['Administrator', 'Purchasing Officer', 'Finance Officer']:
        return render_template('403.html'), 403
    
    try:
        db = get_db()
        orders_data = list(db['orders'].find({}, {'_id': 0}))
        suppliers = list(db['suppliers'].find({}, {'_id': 0}))
        return render_template('purchase_orders.html', orders=orders_data, suppliers=suppliers, role=session.get('role'))
    except Exception as e:
        logger.error(f"Orders error: {e}")
        return render_template('purchase_orders.html', orders=[], suppliers=[], role=session.get('role'))


@app.route('/api/orders', methods=['GET', 'POST'])
@login_required
def api_orders():
    try:
        db = get_db()
        
        if request.method == 'POST':
            data = request.get_json()
            db['orders'].insert_one(data)
            return jsonify({'success': True})
        
        orders_list = list(db['orders'].find({}, {'_id': 0}))
        return jsonify(orders_list)
    except Exception as e:
        logger.error(f"API orders error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders/<po_number>', methods=['PUT'])
@login_required
def update_order(po_number):
    if session.get('role') not in ['Administrator', 'Purchasing Officer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db = get_db()
        data = request.get_json()
        result = db['orders'].update_one({'po_number': po_number}, {'$set': data})
        
        if result.matched_count > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        logger.error(f"Update order error: {e}")
        return jsonify({'error': str(e)}), 500

# ===== PAYMENTS ROUTES =====

@app.route('/payments')
@login_required
@role_check(['Finance Officer', 'Administrator'])
def payments():
    try:
        db = get_db()
        payments_data = list(db['payments'].find({}, {'_id': 0}))
        orders_data = list(db['orders'].find({}, {'_id': 0}))
        return render_template('payments.html', payments=payments_data, orders=orders_data, user_role=session.get('role'))
    except Exception as e:
        logger.error(f"Payments error: {e}")
        return render_template('payments.html', payments=[], orders=[], user_role=session.get('role'))


@app.route('/api/payments', methods=['GET', 'POST'])
@login_required
def api_payments():
    try:
        db = get_db()
        
        if request.method == 'POST':
            data = request.get_json()
            db['payments'].insert_one(data)
            return jsonify({'success': True})
        
        payments_list = list(db['payments'].find({}, {'_id': 0}))
        return jsonify(payments_list)
    except Exception as e:
        logger.error(f"API payments error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/payments/<payment_id>', methods=['PUT'])
@login_required
def update_payment(payment_id):
    if session.get('role') not in ['Administrator', 'Finance Officer']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db = get_db()
        data = request.get_json()
        result = db['payments'].update_one({'id': payment_id}, {'$set': data})
        
        if result.matched_count > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Payment not found'}), 404
    except Exception as e:
        logger.error(f"Update payment error: {e}")
        return jsonify({'error': str(e)}), 500

# ===== FEEDBACK ROUTES =====

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/api/feedback', methods=['GET', 'POST'])
def api_feedback():
    try:
        db = get_db()
        
        if request.method == 'POST':
            data = request.get_json()
            data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            db['feedback'].insert_one(data)
            return jsonify({'success': True})
        
        feedbacks = list(db['feedback'].find({}, {'_id': 0}).sort('date', -1))
        return jsonify(feedbacks)
    except Exception as e:
        logger.error(f"API feedback error: {e}")
        return jsonify({'error': str(e)}), 500


# ===== REPORTS & BACKUP ROUTES =====

@app.route('/backup')
@login_required
def backup():
    try:
        db = get_db()
        suppliers = list(db['suppliers'].find({}, {'_id': 0}))
        orders = list(db['orders'].find({}, {'_id': 0}))
        payments = list(db['payments'].find({}, {'_id': 0}))
        
        return render_template('backup.html',
            suppliers_count=len(suppliers),
            orders_count=len(orders),
            orders_value=sum(o.get('total', 0) for o in orders),
            payments_count=len(payments),
            payments_total=sum(p.get('amount', 0) for p in payments)
        )
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return render_template('backup.html', suppliers_count=0, orders_count=0, orders_value=0, payments_count=0, payments_total=0)


@app.route('/reports')
@login_required
def reports():
    try:
        db = get_db()
        suppliers = list(db['suppliers'].find({}, {'_id': 0}))
        orders = list(db['orders'].find({}, {'_id': 0}))
        payments = list(db['payments'].find({}, {'_id': 0}))
        feedbacks = list(db['feedback'].find({}, {'_id': 0}))
        
        return render_template('reports.html',
            suppliers_count=len(suppliers),
            orders_count=len(orders),
            orders_value=sum(o.get('total', 0) for o in orders),
            payments_count=len(payments),
            payments_total=sum(p.get('amount', 0) for p in payments),
            orders=orders,
            feedbacks=feedbacks
        )
    except Exception as e:
        logger.error(f"Reports error: {e}")
        return render_template('reports.html', suppliers_count=0, orders_count=0, orders_value=0, payments_count=0, payments_total=0, orders=[], feedbacks=[])

# ===== CHART ROUTES =====

@app.route('/api/chart/orders')
@login_required
def chart_orders():
    try:
        db = get_db()
        orders = list(db['orders'].find({}, {'_id': 0}))
        statuses = ['Pending', 'Approved', 'Delivered']
        data = [len([o for o in orders if o.get('status') == s]) for s in statuses]
        return jsonify({'labels': statuses, 'data': data, 'colors': ['#f59e0b', '#3b82f6', '#10b981']})
    except Exception as e:
        logger.error(f"Chart orders error: {e}")
        return jsonify({'labels': [], 'data': [], 'colors': []})


@app.route('/api/chart/suppliers')
@login_required
def chart_suppliers():
    try:
        db = get_db()
        suppliers = list(db['suppliers'].find({}, {'_id': 0}))
        orders = list(db['orders'].find({}, {'_id': 0}))
        labels = [s.get('name', 'Unknown') for s in suppliers]
        data = [len([o for o in orders if o.get('supplier') == s.get('name')]) for s in suppliers]
        return jsonify({'labels': labels, 'data': data, 'colors': ['#2563eb', '#dc2626', '#16a34a']})
    except Exception as e:
        logger.error(f"Chart suppliers error: {e}")
        return jsonify({'labels': [], 'data': [], 'colors': []})

# ===== USER MANAGEMENT ROUTES =====

@app.route('/users')
@login_required
@role_check(['Administrator'])
def users():
    try:
        db = get_db()
        users_list = list(db['users'].find({}, {'_id': 0, 'password': 0}))
        return render_template('users.html', users=users_list)
    except Exception as e:
        logger.error(f"Users error: {e}")
        return render_template('users.html', users=[])


@app.route('/api/users', methods=['GET', 'POST'])
@login_required
@role_check(['Administrator'])
def api_users():
    try:
        db = get_db()
        
        if request.method == 'POST':
            data = request.get_json()
            
            if not data.get('username') or not data.get('password') or not data.get('name') or not data.get('role'):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            existing = db['users'].find_one({'username': data['username']})
            if existing:
                return jsonify({'success': False, 'error': 'Username already exists'}), 400
            
            data['password'] = hash_pwd(data['password'])
            data['status'] = data.get('status', 'Active')
            
            db['users'].insert_one(data)
            user_return = {k: v for k, v in data.items() if k != 'password'}
            return jsonify({'success': True, 'user': user_return})
        
        users_list = list(db['users'].find({}, {'_id': 0, 'password': 0}))
        return jsonify(users_list)
    except Exception as e:
        logger.error(f"API users error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<uid>', methods=['PUT', 'DELETE'])
@login_required
@role_check(['Administrator'])
def api_user(uid):
    try:
        db = get_db()
        user = db['users'].find_one({'username': uid}, {'_id': 0})
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if request.method == 'DELETE':
            db['users'].delete_one({'username': uid})
            return jsonify({'success': True})
        
        elif request.method == 'PUT':
            data = request.get_json() or {}
            
            if data.get('username') and data['username'].lower() != user['username'].lower():
                existing = db['users'].find_one({'username': data['username']})
                if existing:
                    return jsonify({'success': False, 'error': 'Username already exists'}), 400
            
            if data.get('password'):
                data['password'] = hash_pwd(data['password'])
            
            db['users'].update_one({'username': uid}, {'$set': data})
            updated_user = db['users'].find_one({'username': data.get('username', uid)}, {'_id': 0, 'password': 0})
            return jsonify({'success': True, 'user': updated_user})
    except Exception as e:
        logger.error(f"API user error: {e}")
        return jsonify({'error': str(e)}), 500


# ===== SETTINGS ROUTES =====

@app.route('/settings', methods=['GET', 'POST'])
@login_required
@role_check(['Administrator'])
def settings():
    settings_data = load_settings()
    message = None
    
    if request.method == 'POST':
        system_name = request.form.get('system_name', settings_data['system_name']).strip()
        settings_data['system_name'] = system_name or settings_data['system_name']
        
        if 'logo' in request.files:
            logo_file = request.files['logo']
            if logo_file and allowed_file(logo_file.filename):
                filename = secure_filename(logo_file.filename)
                ext = filename.rsplit(".", 1)[1].lower()
                logo_path = f'images/site-logo-{int(datetime.now().timestamp())}.{ext}'
                logo_file.save(os.path.join('static', logo_path))
                settings_data['logo'] = logo_path
        
        if 'background' in request.files:
            bg_file = request.files['background']
            if bg_file and allowed_file(bg_file.filename):
                filename = secure_filename(bg_file.filename)
                ext = filename.rsplit(".", 1)[1].lower()
                bg_path = f'images/homepage-bg-{int(datetime.now().timestamp())}.{ext}'
                bg_file.save(os.path.join('static', bg_path))
                settings_data['homepage_background'] = bg_path
        
        save_settings(settings_data)
        message = 'Settings saved successfully.'
    
    return render_template('settings.html', settings=settings_data, message=message)


# ===== PROFILE ROUTES =====

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
        db = get_db()
        user = db['users'].find_one({'name': session['user']}, {'_id': 0})
        
        if not user:
            return redirect(url_for('logout'))
        
        message = None
        
        if request.method == 'POST':
            data = request.form
            
            if data.get('name'):
                user['name'] = data['name'].strip()
                session['user'] = user['name']
            
            if data.get('username'):
                if data['username'].lower() != user['username'].lower():
                    existing = db['users'].find_one({'username': data['username']})
                    if existing:
                        message = 'Username already exists'
                    else:
                        user['username'] = data['username'].strip()
            
            if data.get('password'):
                user['password'] = hash_pwd(data['password'])
            
            if 'profile_picture' in request.files:
                pic_file = request.files['profile_picture']
                if pic_file and allowed_file(pic_file.filename):
                    filename = secure_filename(pic_file.filename)
                    ext = filename.rsplit(".", 1)[1].lower()
                    pic_path = f'images/profile-{int(datetime.now().timestamp())}.{ext}'
                    pic_file.save(os.path.join('static', pic_path))
                    user['profile_picture'] = pic_path
            
            db['users'].update_one({'name': session['user']}, {'$set': user})
            if not message:
                message = 'Profile updated successfully.'
        
        user.pop('password', None)
        return render_template('profile.html', user=user, message=message)
    except Exception as e:
        logger.error(f"Profile error: {e}")
        return redirect(url_for('logout'))


# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    logger.error(f"Internal error: {error}")
    return render_template('500.html'), 500


if __name__ == '__main__':
    # For local development only
    app.run(debug=os.environ.get('DEBUG', 'False').lower() == 'true')
