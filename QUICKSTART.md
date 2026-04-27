# SPOMS - Quick Start Guide

## 🎯 Overview

SPOMS (Supplier and Purchase Order Management System) is now cloud-ready and uses MongoDB as its database backend.

## 🖥️ Local Development Setup

### 1. Install Python Dependencies

```bash
# Clone or download the project
cd Spoms

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up MongoDB

#### Option A: Use MongoDB Atlas (Cloud - Recommended for Vercel testing)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create account and cluster
3. Create database user
4. Get connection string
5. Copy connection string

#### Option B: Use Local MongoDB (For pure local development)
1. Download and install MongoDB: https://www.mongodb.com/try/download/community
2. Start MongoDB service
3. Connection string: `mongodb://localhost:27017/spoms`

### 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your MongoDB connection string
# For local MongoDB:
MONGODB_URI=mongodb://localhost:27017/spoms
# For MongoDB Atlas:
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/spoms?retryWrites=true&w=majority

# Set other variables
FLASK_ENV=development
SECRET_KEY=your-secret-key-for-development
DEBUG=True
```

### 4. Initialize Database

```bash
python init_db.py
```

Expected output:
```
==================================================
🔧 Initializing SPOMS Database
==================================================

✓ Migrated X records to [collection]
✓ Initialized users
✓ Initialized settings

==================================================
✓ Database initialization completed successfully!
==================================================
```

### 5. Run Application

```bash
# Start Flask development server
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 6. Access Application

Open browser and go to: http://localhost:5000

#### Default Credentials:
| Username | Password | Role |
|----------|----------|------|
| dennis | lopez | Administrator |
| jani | jani | Purchasing Officer |
| angel | angel | Finance Officer |
| jennifer | jennifer | Store Owner |

## 📋 Features

### ✅ Modules Implemented

1. **Supplier Management**
   - Add/Edit/Delete suppliers
   - Search suppliers
   - View supplier details

2. **Purchase Order Management**
   - Create purchase orders
   - Select suppliers
   - Auto-calculate totals
   - Update order status (Pending, Approved, Delivered, Cancelled)

3. **Payment Management**
   - Record supplier payments
   - Select payment methods
   - Update payment status

4. **Reporting**
   - View order reports
   - Track payment history
   - Dashboard statistics
   - Charts and analytics

5. **User Management** (Admin only)
   - Create/Edit/Delete users
   - Assign roles
   - Manage permissions

6. **Settings** (Admin only)
   - Customize system name
   - Upload logo
   - Upload homepage background

7. **Feedback**
   - Users can submit feedback
   - Rate system performance

## 🏗️ Project Structure

```
Spoms/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── database.py            # MongoDB connection & operations
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
├── vercel.json            # Vercel deployment config
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── DEPLOYMENT_GUIDE.md    # Deployment instructions
├── DEPLOYMENT_CHECKLIST.md # Pre-deployment checklist
├── QUICKSTART.md          # This file
├── static/
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Image assets
└── templates/
    ├── base.html          # Base template
    ├── index.html         # Homepage
    ├── login.html         # Login page
    ├── dashboard.html     # Dashboard
    ├── suppliers.html     # Suppliers page
    ├── purchase_orders.html
    ├── payments.html
    ├── reports.html
    ├── users.html
    ├── settings.html
    ├── profile.html
    ├── feedback.html
    ├── 403.html           # Access denied
    ├── 404.html           # Not found
    └── 500.html           # Server error
```

## 🗄️ Database Collections

### Users
```json
{
  "name": "Dennis Lopez Jr",
  "username": "dennis",
  "password": "hashed_password",
  "role": "Administrator",
  "email": "dennis@spoms.com",
  "created_at": "2026-04-27T10:00:00",
  "updated_at": "2026-04-27T10:00:00"
}
```

### Suppliers
```json
{
  "id": "SUP001",
  "name": "Supplier Name",
  "contact": "contact@supplier.com",
  "address": "123 Main St",
  "status": "Active",
  "created_at": "2026-04-27T10:00:00"
}
```

### Orders
```json
{
  "po": "PO001",
  "supplier": "Supplier Name",
  "items": [{"product": "Item", "quantity": 10, "unit_price": 100}],
  "total": 1000,
  "status": "Pending",
  "delivery": "2026-05-01",
  "created_at": "2026-04-27T10:00:00"
}
```

### Payments
```json
{
  "id": "PAY001",
  "po_number": "PO001",
  "amount": 1000,
  "method": "Bank Transfer",
  "status": "Pending",
  "created_at": "2026-04-27T10:00:00"
}
```

## 🔐 Security Notes

⚠️ **Important**:
1. **Change default passwords** after first deployment
2. **Never commit** `.env` files with real secrets
3. **Use strong passwords** for MongoDB users
4. **Enable HTTPS** in production (Vercel handles this)
5. **Regularly backup** MongoDB data

## 🐛 Troubleshooting

### Error: "MONGODB_URI environment variable not set"
```bash
# Solution: Check .env file exists and has MONGODB_URI
cat .env  # On Windows: type .env
```

### Error: "Connection refused to MongoDB"
```bash
# Solution: Start MongoDB service
# For local MongoDB:
# Windows: mongod.exe
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

### Error: "Cannot find module 'pymongo'"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Login fails with "Invalid credentials"
```bash
# Solution: Check if init_db.py was run successfully
python init_db.py  # Run again if needed
```

### Static files not loading (CSS/JS broken)
```bash
# Solution: Restart Flask server
# Press Ctrl+C to stop
python app.py  # Start again
```

## 📱 Testing the System

### Test Login
1. Go to Login page
2. Enter: Username=`dennis`, Password=`lopez`
3. Click Login

### Test Creating Supplier (Admin/Store Owner only)
1. Go to Suppliers page
2. Click "Add Supplier"
3. Fill form and submit

### Test Creating Order (Purchasing Officer only)
1. Go to Orders page
2. Click "Create Order"
3. Select supplier and add items
4. Submit

### Test Dashboard
1. View statistics
2. Check order/payment counts
3. Verify charts display

## 🚀 Deploying to Vercel

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

Quick summary:
1. Create MongoDB Atlas account and cluster
2. Set up Vercel project
3. Configure environment variables
4. Push code to GitHub
5. Deploy to Vercel
6. Initialize database
7. Change default passwords

## 📞 Getting Help

### Documentation
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [Main README](README.MD)

### External Resources
- Flask: https://flask.palletsprojects.com
- MongoDB: https://docs.mongodb.com
- Vercel: https://vercel.com/docs
- PyMongo: https://pymongo.readthedocs.io

### Common Questions

**Q: Can I use SQLite instead of MongoDB?**  
A: Current implementation uses MongoDB for cloud compatibility. To use SQLite, you'd need to refactor database.py and app.py.

**Q: How do I backup my data?**  
A: MongoDB Atlas provides automated backups. For Vercel, configure backup settings in MongoDB dashboard.

**Q: Can multiple users work simultaneously?**  
A: Yes! MongoDB handles concurrent connections. All users see real-time updates.

**Q: How do I add new users?**  
A: Login as Administrator → Users page → Add User

**Q: How do I change system settings?**  
A: Login as Administrator → Settings → Customize

---

**Version**: 1.0 Production Ready  
**Last Updated**: April 2026  
**Status**: ✅ Cloud Ready
