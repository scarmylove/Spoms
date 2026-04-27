# SPOMS - Supplier and Purchase Order Management System

A comprehensive Flask-based management system designed to streamline supplier relationships, purchase order processing, payment tracking, and business intelligence through intuitive dashboards and real-time reporting.

## 👥 Team

- **Dennis Lopez Jr** - Admin
- **John Lester Poquita** - Purchasing Officer
- **Angel Rose Cepe** - Finance Officer
- **Jennifer Urboda** - Store Owner

## 📋 Table of Contents

- [Features](#features)
- [Team](#team)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Architecture](#project-architecture)
- [API Endpoints](#api-endpoints)
- [User Accounts](#user-accounts)
- [Data Storage](#data-storage)
- [Deployment](#deployment)
- [Technologies Used](#technologies-used)

## ✨ Features

### 🏢 Supplier Management
- Add, view, update, and delete suppliers
- Search suppliers by name and status
- Track supplier details and contact information
- Monitor supplier performance

### 📦 Purchase Order Management
- Create and manage purchase orders
- Select suppliers from existing inventory
- Add products with quantities and unit prices
- Automatic calculation of subtotals and totals
- Track order status (Pending, Approved, Delivered, Cancelled)
- Monitor delivery dates

### 💰 Payment Processing
- Record supplier payments
- Support multiple payment methods (Bank Transfer, Check, Cash)
- Track payment status (Pending, Partial, Paid)
- View complete payment history
- Match payments to purchase orders

### 📊 Reporting & Analytics
- Comprehensive purchase order reports
- Orders grouped by status with visual summaries
- Payment status tracking
- Delivery metrics
- Feedback management
- Export and analyze business data

### 👥 User Management
- Role-based access control
- Multiple user roles (Admin, Purchasing Officer, Finance Officer, Store Owner)
- Secure authentication
- User profile management

### 🎨 Dashboard
- Intuitive web-based interface
- Real-time data visualization
- Responsive design
- Easy navigation

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MongoDB (optional - for database version)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Spoms
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   On Windows:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Environment Variables:**
   Create a `.env` file in the root directory (optional for local development):
   ```
   FLASK_ENV=development
   FLASK_DEBUG=True
   MONGODB_URI=your_mongodb_connection_string
   ```

2. **Data Directory:**
   The application automatically creates a `data/` directory for JSON storage:
   ```
   data/
   ├── users.json
   ├── suppliers.json
   ├── orders.json
   ├── payments.json
   ├── feedback.json
   └── settings.json
   ```

### Running the Application

1. **Start the Flask development server:**
   ```bash
   python app.py
   ```

2. **Access the application:**
   Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. **Login with demo credentials:**
   - **Admin**: dennis / lopez
   - **Purchasing Officer**: jani / jani
   - **Finance Officer**: angel / angel
   - **Store Owner**: jennifer / jennifer

## 🏗️ Project Architecture

### Directory Structure

```
Spoms/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── database.py            # Database/data access layer
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── DEPLOYMENT_GUIDE.md   # Deployment instructions
├── QUICKSTART.md         # Quick start guide
├── DEPLOYMENT_CHECKLIST.md # Pre-deployment checklist
│
├── data/                 # JSON data storage
│   ├── users.json
│   ├── suppliers.json
│   ├── orders.json
│   ├── payments.json
│   ├── feedback.json
│   └── settings.json
│
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   │   ├── style.css
│   │   ├── auth.css
│   │   ├── dashboard.css
│   │   └── homepage.css
│   ├── js/              # JavaScript files
│   │   ├── app.js
│   │   ├── charts.js
│   │   ├── payments.js
│   │   ├── purchase_orders.js
│   │   ├── suppliers.js
│   │   ├── users.js
│   │   └── animations.js
│   └── images/          # Images and logos
│
└── templates/            # HTML templates
    ├── base.html
    ├── index.html
    ├── login.html
    ├── dashboard.html
    ├── suppliers.html
    ├── purchase_orders.html
    ├── payments.html
    ├── reports.html
    ├── profile.html
    ├── feedback.html
    ├── settings.html
    ├── users.html
    ├── orders.html
    └── backup.html
```

### Core Modules

#### Module 1: Supplier Management
- **Route**: `/suppliers`
- **Template**: `templates/suppliers.html`
- **Data**: `data/suppliers.json`
- **API Endpoints**:
  - `GET /api/suppliers` - Retrieve all suppliers
  - `POST /api/suppliers` - Create new supplier
  - `PUT /api/suppliers/<sid>` - Update supplier
  - `DELETE /api/suppliers/<sid>` - Delete supplier

#### Module 2: Purchase Order Management
- **Route**: `/orders`
- **Template**: `templates/purchase_orders.html`
- **Data**: `data/orders.json`
- **API Endpoints**:
  - `GET /api/orders` - Retrieve all orders
  - `POST /api/orders` - Create new order
  - `PUT /api/orders/<po_number>` - Update order
- **Features**: Status tracking (Pending, Approved, Delivered, Cancelled), automatic calculations

#### Module 3: Payment Processing
- **Route**: `/payments`
- **Template**: `templates/payments.html`
- **Data**: `data/payments.json`
- **API Endpoints**:
  - `GET /api/payments` - Retrieve all payments
  - `POST /api/payments` - Record payment
  - `PUT /api/payments/<payment_id>` - Update payment status
- **Payment Methods**: Bank Transfer, Check, Cash
- **Status Tracking**: Pending, Partial, Paid

#### Module 4: Reporting & Analytics
- **Route**: `/reports`
- **Template**: `templates/reports.html`
- **Data Source**: Aggregated from orders, payments, and suppliers
- **Reports**:
  - Purchase order summary by status
  - Payment status overview
  - Supplier performance metrics
  - Delivery tracking

#### Module 5: User Management
- **Route**: `/users`
- **Template**: `templates/users.html`
- **Data**: `data/users.json`
- **Features**: Role-based access, profile management

## 📡 API Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /profile` - User profile

### Suppliers
- `GET /api/suppliers` - List all suppliers
- `POST /api/suppliers` - Create supplier
- `PUT /api/suppliers/<sid>` - Update supplier
- `DELETE /api/suppliers/<sid>` - Delete supplier

### Purchase Orders
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create order
- `PUT /api/orders/<po_number>` - Update order

### Payments
- `GET /api/payments` - List all payments
- `POST /api/payments` - Record payment
- `PUT /api/payments/<payment_id>` - Update payment status

### Reports
- `GET /reports` - View reports

## 👤 User Accounts

The system includes four pre-configured user accounts:

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Admin | dennis | lopez | Full system access |
| Purchasing Officer | jani | jani | Create/manage orders |
| Finance Officer | angel | angel | Payment management |
| Store Owner | jennifer | jennifer | Inventory access |

**To add new users**: Edit `data/users.json` directly or use the user management interface.

## 💾 Data Storage

The application uses JSON files for data persistence:

- **users.json**: User accounts and authentication
- **suppliers.json**: Supplier information
- **orders.json**: Purchase order records
- **payments.json**: Payment transactions
- **feedback.json**: Customer feedback
- **settings.json**: System configuration

All data is automatically loaded/saved in the `data/` directory.

## 🚀 Deployment

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

### Quick Deployment Options

- **Vercel**: Configuration included in `vercel.json`
- **Docker**: Standard Python/Flask containerization
- **Traditional Server**: Python with Gunicorn or similar WSGI server

### Pre-Deployment Checklist

Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) before deploying to production.

## 🛠️ Technologies Used

- **Backend**: Flask 2.3.3
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: JSON (local), MongoDB (optional)
- **Server**: Gunicorn
- **Authentication**: SHA-256 password hashing
- **Environment Management**: python-dotenv
- **ORM**: PyMongo (optional)

## 📝 Additional Resources

- [Quick Start Guide](QUICKSTART.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Change Log](CHANGES.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)


