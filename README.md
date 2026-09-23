# QuicklyCart

### Multi-vendor local commerce and last-mile delivery platform built with Django

QuicklyCart is a Django-based e-commerce marketplace project designed around the full flow from product discovery to delivery. The application supports customers, sellers, delivery riders, and administrators, with product management, cart operations, checkout, order handling, seller/rider verification, and rider workflow features.

---

## Core idea

Instead of treating an online store as only a product catalogue, this project models several roles involved in a delivery marketplace:

```text
Customer
   │
   ├── Browse products
   ├── Add to cart
   ├── Checkout
   └── Place / view orders
   │
   ▼
Seller
   │
   ├── Apply / verify documents
   ├── Manage products
   └── Update order status
   │
   ▼
Rider
   │
   ├── Register
   ├── Submit documents
   └── Participate in delivery workflow
   │
   ▼
Admin
   ├── Manage users
   ├── Verify sellers
   ├── Verify riders
   └── Manage categories / reporting UI
```

---

## Main features

### Customer

- Account registration
- Email OTP verification
- Login and logout
- Forgot-password OTP flow
- Profile management
- Profile image upload
- Product browsing
- Product detail pages
- Related product suggestions
- Category and sub-category filtering
- Search/filter UI
- Shopping cart
- Add, update, and remove cart items
- Buy-now flow
- Address selection
- Checkout flow
- Cash on Delivery order placement
- Order history
- Product reviews and ratings UI
- Local cart state with `localStorage`

### Seller

- Seller registration
- Email OTP verification
- Seller document submission
- GST number capture
- Seller approval / rejection by admin
- Seller dashboard
- Product creation
- Multiple product image uploads
- Product update
- Product deletion
- Category selection
- Inventory/stock fields
- Seller-specific order listing
- Order status updates

### Delivery rider

- Rider registration
- Email OTP verification
- Profile image upload
- ID proof upload
- Driving licence upload
- RC book upload
- Rider application status
- Rider rules/information page
- Admin verification / rejection
- Delivery-oriented rider model and order-event structure

### Admin

- Dashboard statistics
- User management
- Seller management
- Rider management
- Seller document verification UI
- Rider document verification UI
- Approve / reject workflows
- Rejection reason capture
- Category management
- Main category / sub-category support
- Category image upload
- Report-preview UI for users, sellers, and riders

---

## Commerce flow

### Product flow

```text
Category
   ↓
Product listing
   ↓
Product details
   ↓
Add to cart / Buy now
   ↓
Address
   ↓
Checkout
   ↓
Order
```

### Cart flow

The frontend keeps a synchronized cart representation in `localStorage`, while the backend exposes endpoints for:

```text
POST /cart/add/
POST /cart/update/
POST /cart/remove/
```

This lets the UI update quantities and totals quickly while also syncing cart changes with Django.

---

## Order flow

The current checkout implementation supports:

- Cart checkout
- Buy-now checkout
- Address selection
- Discount calculation
- Delivery fee display
- Cash on Delivery
- Order creation
- Cart clearing after order placement
- Seller-side status updates
- Customer order history

The current payment screen contains UI for UPI, card, and COD, but the backend order-placement implementation currently creates orders for **COD**. There is no production payment gateway integration in the supplied source.

---

## Seller verification flow

```text
Seller registration
      ↓
Email OTP
      ↓
Submit business documents
      ↓
Admin review
   ↙       ↘
Approve   Reject + reason
```

Seller verification information is stored using JSON fields for uploaded document metadata and per-document verification state.

---

## Rider verification flow

Riders submit:

- Identity proof
- Driving licence
- RC book

The admin interface provides document review controls and records approval/rejection information.

```text
Rider application
      ↓
OTP verification
      ↓
Pending
      ↓
Admin document review
   ↙       ↘
Approved   Rejected
```

---

## Data models

The main Django models are:

| Model | Purpose |
|---|---|
| `User` | Customer, seller, and rider account information |
| `Seller` | Seller application, documents, status, and verification |
| `Warehouse` | Seller warehouse information |
| `Product` | Product catalogue data |
| `Order` | Customer orders |
| `Addtocart` | Server-side cart records |
| `Rider` | Delivery rider profile and verification |
| `Category` | Hierarchical product categories |
| `RiderOrder` | Rider delivery/order event history |

The database relationships are primarily handled through Django `ForeignKey` fields.

---

## Project structure

```text
QuicklyCart/
├── QuicklyCart/
│   ├── settings.py
│   ├── urls.py
│   ├── view.py
│   ├── asgi.py
│   └── wsgi.py
│
├── QuicklyCart_app/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
│
├── templates/
│   ├── index.html
│   ├── product.html
│   ├── orders.html
│   ├── payment.html
│   ├── profile.html
│   ├── seller.html
│   ├── seller_home.html
│   ├── delivery.html
│   ├── rider_home.html
│   ├── rider_rules.html
│   ├── rider_otp_verification.html
│   ├── admin.html
│   └── ...
│
├── static/
│   ├── css/
│   └── images/
│
├── docs/
│   └── assets/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Technology stack

| Area | Technology |
|---|---|
| Backend | Python / Django |
| Django version | 5.2.4 |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Templates | Django Template Language |
| Styling | Custom CSS |
| Session state | Django sessions |
| Client cart | Browser `localStorage` |
| Email verification | SMTP + OTP |
| File uploads | Django `FileSystemStorage` |
| ORM | Django ORM |

The supplied migrations were generated by Django **5.2.4**, which is why that version is used in the repository requirements.

---

## Requirements

- Python 3.10+ recommended
- Django 5.2.4
- A modern web browser
- SMTP credentials if email OTP features are enabled

Because the project is a Django application, the recommended development setup is a Python virtual environment.

---

## Installation

### 1. Clone the repository

```bash
git clone ...
cd QuicklyCart
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy:

```text
.env.example
```

to your local environment configuration and set the values required by your setup.

At minimum:

```text
DJANGO_SECRET_KEY=replace-this
DJANGO_DEBUG=1

EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

The repository version of `settings.py` does not contain the original SMTP password.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an admin account

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## Static files and uploads

The project stores product/category/profile uploads under:

```text
static/images/
```

For a production deployment, uploaded media should normally be separated from application static assets.

A cleaner production structure would be:

```text
static/     → CSS, JS, fixed assets
media/      → user/product uploads
```

---

## Email OTP

The project uses SMTP to send one-time passwords for:

- User registration
- Seller registration
- Rider registration
- Password recovery

The OTP is temporarily stored in the Django session and then checked during verification.

For local development with Gmail SMTP, use a dedicated app password rather than a normal account password.

---

## Authentication

Passwords created through the registration flows are passed through Django's password hashing helper before being stored.

The application uses its own `User` model and session keys such as:

```text
user_id
user_email
user_name
```

rather than Django's standard `AbstractUser` / `AuthenticationMiddleware` flow.

A future refactor could move the project to Django's built-in authentication framework for stronger consistency and permission handling.

---

## Category system

Categories are hierarchical:

```text
Main Category
    ├── Sub-category
    ├── Sub-category
    └── Sub-category
```

The `Category` model uses a self-referencing foreign key:

```python
parent = models.ForeignKey(
    'self',
    ...
)
```

This allows the admin side to manage main categories and their subcategories.

---

## Seller product management

Sellers can create products with:

- Name
- Price
- Stock quantity
- Description
- Main category
- Sub-category
- Multiple images

Products belong to a seller using a foreign key relationship.

The product details page also loads related products from the same main category.

---

## Admin dashboard

The admin interface includes dashboard statistics for:

- Total users
- Total sellers
- Pending sellers
- Total riders
- Approved/online rider count
- Revenue calculation
- Active orders

It also provides interfaces for seller/rider verification and category management.

---

## What this project demonstrates

This project shows practical experience with:

- Django project structure
- Django ORM
- Relational data modelling
- Foreign-key relationships
- Session-based application flows
- Authentication and password hashing
- OTP workflows
- File uploads
- Multi-role business logic
- E-commerce cart design
- Checkout and order creation
- Seller onboarding
- Admin verification workflows
- Rider onboarding
- Product/category management
- Frontend JavaScript interactions
- REST-like JSON endpoints

---

## Development notes

The supplied project contains Django migrations created across several development stages, including seller, category, rider, rider verification, and rider model changes.

The GitHub-ready copy intentionally excludes:

```text
db.sqlite3
__pycache__/
*.pyc
runtime upload artefacts
```

so the repository stays focused on source code and reproducible project setup.

---

## Project status

**Academic / Portfolio Project**

QuicklyCart is a multi-role e-commerce and delivery-management application developed for learning and demonstrating full-stack Django concepts.

---

## License

MIT
