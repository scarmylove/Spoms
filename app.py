from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import hashlib
from config import config
from database import (
    get_db,
    find_document,
    find_documents,
    save_document,
    update_document,
    delete_document,
    load_collection
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config)

# Ensure directories exist
os.makedirs('static/images', exist_ok=True)

# Initialize database connection
try:
    get_db()
    logger.info("Database connection established")
except Exception as e:
    logger.warning(f"Database connection failed: {e}. Using fallback mode.")



def hash_pwd(pwd):
    """Hash password using SHA256"""
    return hashlib.sha256(pwd.encode()).hexdigest()


def allowed_file(filename):
    """Check if file is allowed for upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'svg'}


def default_settings():
    """Return default system settings"""
    return {
        'system_name': 'SPOMS',
        'logo': 'images/spoms.png',
        'homepage_background': 'images/spoms.png'
    }


def load_settings():
    """Load system settings from database"""
    try:
        settings = find_document('settings', {})
        if not settings:
            settings = default_settings()
            settings['created_at'] = datetime.now().isoformat()
            save_document('settings', settings)
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return default_settings()


def save_settings(settings):
    """Save system settings to database"""
    try:
        settings['updated_at'] = datetime.now().isoformat()
        update_document('settings', {}, settings)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")




@app.context_processor
def inject_settings():
    """Make settings available in all templates"""
    return {'settings': load_settings()}


@app.context_processor
def inject_current_user():
    """Make current user available in all templates"""
    if 'user' in session:
        try:
            user = find_document('users', {'name': session['user']})
            return {'current_user': user}
        except Exception as e:
            logger.error(f"Error loading current user: {e}")
    return {'current_user': None}


# ===== DECORATORS =====
def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def role_check(roles):
    """Decorator to check user role"""
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
    """Home page"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            user = find_document('users', {'username': username})
            
            if user and user.get('password') == hash_pwd(password):
                session['user'] = user['name']
                session['role'] = user.get('role', 'User')
                return redirect(url_for('dashboard'))
            
            return render_template('login.html', error='Invalid credentials')
        except Exception as e:
            logger.error(f"Login error: {e}")
            return render_template('login.html', error='An error occurred during login')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for('home'))



# ===== DASHBOARD ROUTE =====
@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with statistics"""
    try:
        suppliers = load_collection('suppliers')
        orders = load_collection('orders')
        payments = load_collection('payments')
        
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
    """View suppliers page"""
    if session.get('role') not in ['Administrator', 'Purchasing Officer', 'Store Owner']:
        return render_template('403.html'), 403
    try:
        data = load_collection('suppliers')
        return render_template('suppliers.html', suppliers=data, role=session.get('role'))
    except Exception as e:
        logger.error(f"Suppliers page error: {e}")
        return render_template('suppliers.html', suppliers=[], role=session.get('role'))


@app.route('/api/suppliers', methods=['GET', 'POST'])
@login_required
def api_suppliers():
    """API for suppliers CRUD"""
    try:
        if request.method == 'POST':
            if session.get('role') not in ['Administrator', 'Store Owner']:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
            data = request.json
            data['created_at'] = datetime.now().isoformat()
            save_document('suppliers', data)
            return jsonify({'success': True})
        
        suppliers = load_collection('suppliers')
        return jsonify(suppliers)
    except Exception as e:
        logger.error(f"Suppliers API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/suppliers/<sid>', methods=['DELETE', 'PUT'])
@login_required
@role_check(['Administrator', 'Store Owner'])
def api_supplier(sid):
    """Update or delete supplier"""
    try:
        if request.method == 'DELETE':
            delete_document('suppliers', {'id': sid})
            return jsonify({'success': True})
        
        elif request.method == 'PUT':
            data = request.json
            data['updated_at'] = datetime.now().isoformat()
            update_document('suppliers', {'id': sid}, data)
            return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Supplier API error: {e}")
        return jsonify({'error': str(e)}), 500



# ===== ORDERS ROUTES =====
@app.route('/orders')
@login_required
def orders():
    """View orders page"""
    if session.get('role') not in ['Administrator', 'Purchasing Officer', 'Finance Officer']:
        return render_template('403.html'), 403
    try:
        data = load_collection('orders')
        suppliers = load_collection('suppliers')
        return render_template('purchase_orders.html', orders=data, suppliers=suppliers, role=session.get('role'))
    except Exception as e:
        logger.error(f"Orders page error: {e}")
        return render_template('purchase_orders.html', orders=[], suppliers=[], role=session.get('role'))


@app.route('/api/orders', methods=['GET', 'POST'])
@login_required
def api_orders():
    """API for orders CRUD"""
    try:
        if request.method == 'POST':
            data = request.json
            data['created_at'] = datetime.now().isoformat()
            save_document('orders', data)
            return jsonify({'success': True})
        
        orders = load_collection('orders')
        return jsonify(orders)
    except Exception as e:
        logger.error(f"Orders API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders/<po_number>', methods=['PUT'])
@login_required
@role_check(['Administrator', 'Purchasing Officer'])
def update_order(po_number):
    """Update order"""
    try:
        data = request.json
        data['updated_at'] = datetime.now().isoformat()
        result = update_document('orders', {'po': po_number}, data)
        
        if result > 0:
            return jsonify({'success': True})
        return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        logger.error(f"Order update error: {e}")
        return jsonify({'error': str(e)}), 500



# ===== PAYMENTS ROUTES =====
@app.route('/payments')
@login_required
@role_check(['Finance Officer', 'Administrator'])
def payments():
    """View payments page"""
    try:
        data = load_collection('payments')
        orders = load_collection('orders')
        return render_template('payments.html', payments=data, orders=orders, user_role=session.get('role'))
    except Exception as e:
        logger.error(f"Payments page error: {e}")
        return render_template('payments.html', payments=[], orders=[], user_role=session.get('role'))


@app.route('/api/payments', methods=['GET', 'POST'])
@login_required
def api_payments():
    """API for payments CRUD"""
    try:
        if request.method == 'POST':
            data = request.json
            data['created_at'] = datetime.now().isoformat()
            save_document('payments', data)
            return jsonify({'success': True})
        
        payments = load_collection('payments')
        return jsonify(payments)
    except Exception as e:
        logger.error(f"Payments API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/payments/<payment_id>', methods=['PUT'])
@login_required
@role_check(['Administrator', 'Finance Officer'])
def update_payment(payment_id):
    """Update payment"""
    try:
        data = request.json
        data['updated_at'] = datetime.now().isoformat()
        result = update_document('payments', {'id': payment_id}, data)
        
        if result > 0:
            return jsonify({'success': True})
        return jsonify({'error': 'Payment not found'}), 404
    except Exception as e:
        logger.error(f"Payment update error: {e}")
        return jsonify({'error': str(e)}), 500


# ===== FEEDBACK ROUTES =====
@app.route('/feedback')
def feedback():
    """Feedback page"""
    return render_template('feedback.html')


@app.route('/api/feedback', methods=['GET', 'POST'])
def api_feedback():
    """API for feedback"""
    try:
        if request.method == 'POST':
            data = request.json
            feedback_doc = {
                "name": data.get('name', 'Anonymous'),
                "message": data.get('message', ''),
                "rating": data.get('rating', 0),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            save_document('feedback', feedback_doc)
            return jsonify({"success": True})
        
        feedbacks = load_collection('feedback')
        return jsonify(feedbacks)
    except Exception as e:
        logger.error(f"Feedback API error: {e}")
        return jsonify({'error': str(e)}), 500


# ===== REPORTS ROUTES =====
@app.route('/backup')
@login_required
def backup():
    """Backup/Statistics page"""
    try:
        suppliers = load_collection('suppliers')
        orders = load_collection('orders')
        payments = load_collection('payments')
        
        return render_template('backup.html',
            suppliers_count=len(suppliers),
            orders_count=len(orders),
            orders_value=sum(float(o.get('total', 0)) for o in orders),
            payments_count=len(payments),
            payments_total=sum(float(p.get('amount', 0)) for p in payments)
        )
    except Exception as e:
        logger.error(f"Backup page error: {e}")
        return render_template('backup.html', suppliers_count=0, orders_count=0, orders_value=0, payments_count=0, payments_total=0)


@app.route('/reports')
@login_required
def reports():
    """Reports page"""
    try:
        suppliers = load_collection('suppliers')
        orders = load_collection('orders')
        payments = load_collection('payments')
        feedbacks = load_collection('feedback')
        
        return render_template('reports.html',
            suppliers_count=len(suppliers),
            orders_count=len(orders),
            orders_value=sum(float(o.get('total', 0)) for o in orders),
            payments_count=len(payments),
            payments_total=sum(float(p.get('amount', 0)) for p in payments),
            orders=orders,
            feedbacks=feedbacks
        )
    except Exception as e:
        logger.error(f"Reports page error: {e}")
        return render_template('reports.html', suppliers_count=0, orders_count=0, orders_value=0, payments_count=0, payments_total=0, orders=[], feedbacks=[])


# ===== CHART ROUTES =====
@app.route('/api/chart/orders')
@login_required
def chart_orders():
    """Orders chart data"""
    try:
        orders = load_collection('orders')
        statuses = ['Pending', 'Approved', 'Delivered']
        data = [len([o for o in orders if o.get('status') == s]) for s in statuses]
        return jsonify({'labels': statuses, 'data': data, 'colors': ['#f59e0b', '#3b82f6', '#10b981']})
    except Exception as e:
        logger.error(f"Chart orders error: {e}")
        return jsonify({'labels': [], 'data': [], 'colors': []})


@app.route('/api/chart/suppliers')
@login_required
def chart_suppliers():
    """Suppliers chart data"""
    try:
        suppliers = load_collection('suppliers')
        orders = load_collection('orders')
        labels = [s.get('name', 'Unknown') for s in suppliers]
        data = [len([o for o in orders if o.get('supplier') == s.get('name')]) for s in suppliers]
        return jsonify({'labels': labels, 'data': data, 'colors': ['#2563eb', '#dc2626', '#16a34a']})
    except Exception as e:
        logger.error(f"Chart suppliers error: {e}")
        return jsonify({'labels': [], 'data': [], 'colors': []})



# ===== USERS ROUTES =====
@app.route('/users')
@login_required
@role_check(['Administrator'])
def users():
    """Users management page"""
    try:
        data = load_collection('users')
        # Remove passwords from response
        for u in data:
            u.pop('password', None)
        return render_template('users.html', users=data)
    except Exception as e:
        logger.error(f"Users page error: {e}")
        return render_template('users.html', users=[])


@app.route('/api/users', methods=['GET', 'POST'])
@login_required
@role_check(['Administrator'])
def api_users():
    """API for users CRUD"""
    try:
        if request.method == 'POST':
            data = request.json
            
            # Validate required fields
            if not all(data.get(field) for field in ['username', 'password', 'name', 'role']):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            # Check if username exists
            if find_document('users', {'username': data['username']}):
                return jsonify({'success': False, 'error': 'Username already exists'}), 400
            
            data['password'] = hash_pwd(data['password'])
            data['status'] = data.get('status', 'Active')
            data['created_at'] = datetime.now().isoformat()
            
            save_document('users', data)
            return jsonify({'success': True, 'user': {
                'name': data['name'],
                'username': data['username'],
                'role': data['role'],
                'status': data['status']
            }})
        
        users_data = load_collection('users')
        for u in users_data:
            u.pop('password', None)
        return jsonify(users_data)
    except Exception as e:
        logger.error(f"Users API error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/<uid>', methods=['PUT', 'DELETE'])
@login_required
@role_check(['Administrator'])
def api_user(uid):
    """Update or delete user"""
    try:
        user = find_document('users', {'user_id': uid})
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        if request.method == 'DELETE':
            delete_document('users', {'user_id': uid})
            return jsonify({'success': True})
        
        data = request.json or {}
        
        # Check username uniqueness
        if data.get('username') and data['username'].lower() != user['username'].lower():
            if find_document('users', {'username': data['username']}):
                return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        # Update allowed fields
        update_fields = {}
        for field in ['name', 'username', 'role', 'status']:
            if field in data:
                update_fields[field] = data[field]
        
        if data.get('password'):
            update_fields['password'] = hash_pwd(data['password'])
        
        update_fields['updated_at'] = datetime.now().isoformat()
        update_document('users', {'user_id': uid}, update_fields)
        
        return jsonify({'success': True, 'user': {
            'user_id': user['user_id'],
            'name': update_fields.get('name', user['name']),
            'username': update_fields.get('username', user['username']),
            'role': update_fields.get('role', user['role']),
            'status': update_fields.get('status', user['status'])
        }})
    except Exception as e:
        logger.error(f"User API error: {e}")
        return jsonify({'error': str(e)}), 500



# ===== SETTINGS ROUTES =====
@app.route('/settings', methods=['GET', 'POST'])
@login_required
@role_check(['Administrator'])
def settings():
    """System settings page"""
    try:
        current_settings = load_settings()
        message = None
        
        if request.method == 'POST':
            system_name = request.form.get('system_name', '').strip()
            if system_name:
                current_settings['system_name'] = system_name
            
            if 'logo' in request.files:
                logo_file = request.files['logo']
                if logo_file and allowed_file(logo_file.filename):
                    filename = secure_filename(logo_file.filename)
                    logo_path = f'images/site-logo-{int(datetime.now().timestamp())}.{filename.rsplit(".", 1)[1].lower()}'
                    logo_file.save(os.path.join('static', logo_path))
                    current_settings['logo'] = logo_path
            
            if 'background' in request.files:
                bg_file = request.files['background']
                if bg_file and allowed_file(bg_file.filename):
                    filename = secure_filename(bg_file.filename)
                    bg_path = f'images/homepage-bg-{int(datetime.now().timestamp())}.{filename.rsplit(".", 1)[1].lower()}'
                    bg_file.save(os.path.join('static', bg_path))
                    current_settings['homepage_background'] = bg_path
            
            save_settings(current_settings)
            message = 'Settings saved successfully.'
        
        return render_template('settings.html', settings=current_settings, message=message)
    except Exception as e:
        logger.error(f"Settings page error: {e}")
        return render_template('settings.html', settings=default_settings(), message=f"Error: {str(e)}")


# ===== PROFILE ROUTES =====
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    try:
        user = find_document('users', {'name': session['user']})
        
        if not user:
            return redirect(url_for('logout'))
        
        message = None
        
        if request.method == 'POST':
            update_fields = {}
            
            if request.form.get('name'):
                new_name = request.form['name'].strip()
                update_fields['name'] = new_name
                session['user'] = new_name
            
            if request.form.get('username'):
                new_username = request.form['username'].strip()
                if new_username.lower() != user['username'].lower():
                    if find_document('users', {'username': new_username}):
                        message = 'Username already exists'
                    else:
                        update_fields['username'] = new_username
            
            if request.form.get('password'):
                update_fields['password'] = hash_pwd(request.form['password'])
            
            if 'profile_picture' in request.files:
                pic_file = request.files['profile_picture']
                if pic_file and allowed_file(pic_file.filename):
                    filename = secure_filename(pic_file.filename)
                    pic_path = f'images/profile-{user.get("user_id", "user")}-{int(datetime.now().timestamp())}.{filename.rsplit(".", 1)[1].lower()}'
                    pic_file.save(os.path.join('static', pic_path))
                    update_fields['profile_picture'] = pic_path
            
            if update_fields:
                update_fields['updated_at'] = datetime.now().isoformat()
                update_document('users', {'name': session['user']}, update_fields)
                if not message:
                    message = 'Profile updated successfully.'
        
        return render_template('profile.html', user=user, message=message)
    except Exception as e:
        logger.error(f"Profile page error: {e}")
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
    app.run(debug=app.config['DEBUG'])