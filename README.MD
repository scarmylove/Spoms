# SPOMS - Supplier and Purchase Order Management System

A Flask-based Supplier and Purchase Order Management System built to manage suppliers, purchase orders, payments, and reports using Firebase Firestore. We connected it to firebase in order to have a database and to make our system more useful and accessable.

## Team Members

- Dennis Lopez Jr
- John Lester Poquita
- Angel Rose Cepe
- Jennifer Urboda

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone or download the project to your local machine.

2. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

3. Activate the virtual environment:

   ```powershell
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

5. Set up Firebase Firestore:

   ```powershell
   python setup_firestore.py
   ```

## Default User Accounts

Use these credentials to log in:

| Role | Username | Password |
|------|----------|----------|
| Admin | dennis | lopez |
| Admin | reyGodmalin | reyGodmalin |
| Purchasing Officer | jani | jani |
| Finance Officer | angel | angel |
| Store Owner | jennifer | jennifer |

## Project Modules

### Module 1: Supplier Management

This module is implemented and functional in the current code.

**Features:**
- Add new supplier
- View supplier list
- Update supplier information
- Delete supplier
- Search suppliers by text and status
- Display supplier details in the supplier list

**How it works:**
- The `suppliers` route loads supplier data from Firebase Firestore.
- `templates/suppliers.html` provides a searchable table and modal form for add/edit.
- The API endpoints `/api/suppliers` and `/api/suppliers/<sid>` handle create, update, and delete actions.

### Module 2: Purchase Order Management

This module is implemented and functional in the current code.

**Features:**
- Create new purchase order
- Select supplier from existing suppliers
- Add product/item and quantity
- Enter unit price
- Automatically compute subtotal and total
- Update order details/status
- Cancel purchase order via status field
- Track order status as Pending, Approved, Delivered, or Cancelled

**How it works:**
- The `orders` route loads data from Firebase Firestore.
- `templates/purchase_orders.html` provides a creation modal, order table, search, and status update interface.
- The API endpoints `/api/orders` and `/api/orders/<po_number>` handle order creation and updating.

### Module 3: Delivery and Receiving

This module is partially implemented through order status management.

**Implemented behavior:**
- Delivered items are tracked by the order `status` field.
- The `delivery` field records the expected or actual delivery date.
- Order completion is verified by setting status to `Delivered`.
- Delivery status can be updated through the order status edit workflow.

**Note:**
- There is no separate dedicated delivery-only route or receiving form in the current code.
- Delivery handling is currently integrated into purchase order status updates.

### Module 4: Payment Method Management

This module is implemented and functional in the current code.

**Features:**
- Record supplier payment
- Select payment method (`Bank Transfer`, `Check`, `Cash`)
- Update payment status (`Pending`, `Partial`, `Paid`)
- View payment history and status in a searchable table

**How it works:**
- The `payments` route loads data from Firebase Firestore.
- `templates/payments.html` provides a payment-record modal, order selection, auto-fill supplier/total amount, and status editing.
- The API endpoints `/api/payments` and `/api/payments/<payment_id>` handle payment create and status updates.

### Module 5: Reporting

This module is implemented and functional in the current code.

**Features:**
- Purchase order reporting
- Displays orders grouped by status
- Summarizes totals for pending, delivered, and approved orders
- Excludes cancelled orders from the main purchase order report table

**How it works:**
- The `reports` route loads orders, payments, suppliers, and feedback data from Firebase Firestore.
- `templates/reports.html` renders a report table and summary metrics derived from current order data.

## Running the Application

1. Make sure your virtual environment is activated (see Installation section).

2. Start the Flask application:

   ```powershell
   python app.py
   ```

3. Open your browser and navigate to:

   ```text
   http://localhost:5000
   ```

4. Log in using one of the default accounts listed above.

5. Use the navigation menu to access different modules:
   - **Suppliers** - Manage supplier information
   - **Purchase Orders** - Create and track orders
   - **Payments** - Record and track supplier payments
   - **Reports** - View analytics and summaries
   - **Users** - Manage user accounts (Admin only)
   - **Settings** - Configure system settings

## Project Structure

```
Spoms/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── firebase_config.py    # Firebase Firestore configuration
├── firebase-key.json     # Firebase service account credentials
├── setup_firestore.py    # Firestore initialization script
├── requirements.txt      # Python dependencies
├── static/              # Static files (CSS, JS, images)
│   ├── css/
│   ├── images/
│   └── js/
└── templates/           # HTML templates
```

## Technical Notes

### Data Storage
- All application data is stored in Firebase Firestore
- Data is synced in real-time across all application instances
- Requires valid Firebase credentials (`firebase-key.json`) to initialize

### Architecture
- **Backend:** Flask web framework (Python)
- **Frontend:** HTML5, CSS3, JavaScript with responsive design
- **Data Layer:** Firebase Firestore (NoSQL database)
- **Authentication:** Username/password authentication stored in Firebase Firestore

### Current Limitations
- No product/item master module; products are entered directly on purchase orders
- Delivery and receiving are managed through order status updates rather than a dedicated workflow
- Authentication uses basic username/password (no encryption); for production, implement secure authentication
- Single-threaded; not optimized for concurrent users



## Troubleshooting

**Port 5000 already in use:**
```powershell
python app.py --port 5001
```

**Firebase connection issues:**
- Verify `firebase-key.json` exists and is valid
- Check Firebase project credentials in `firebase_config.py`
- Ensure your Firebase project has Firestore enabled

## Deployment

The system is deployed in vercel. Just copy the domain sir.
 ```text
   spom-system.vercel.app
   ```

