# VNT PhoneStore

VNT PhoneStore is a portfolio e-commerce application I built with Django to demonstrate end-to-end product development for an online smartphone store. The project covers both the customer journey and the back-office workflow: browsing products, managing a cart, completing checkout, and handling catalog and order operations from a staff dashboard.

## Recruiter Summary

If you are reviewing this repository as a recruiter, the main signals in this project are:

- I can build a complete CRUD-based web application with a clear domain model.
- I can implement real business flows, not just static pages.
- I understand authentication, role-based access, session handling, and transactional data updates.
- I can organize a Django codebase into separate apps for accounts, products, cart, orders, storefront, and dashboard logic.

## What The Application Does

- Public storefront with featured products, category pages, product detail pages, and search.
- Customer registration and login with flexible authentication using phone number, email, or username.
- Shopping cart flow with support for session-based carts and database-backed carts for authenticated users.
- Cart merge logic that preserves guest selections after login.
- Checkout flow with delivery or in-store pickup options.
- Payment options for cash on delivery, e-wallet/ATM, and bank transfer with VietQR support.
- Order creation that also writes order items and updates stock levels.
- Staff dashboard for managing categories, brands, products, customers, and order status.
- Separate session cookies for storefront and dashboard access so admin and customer sessions do not interfere with each other.

## Technical Highlights

- Custom `User` model with role, phone number, and profile fields.
- Transaction-safe checkout using Django database transactions.
- Order status lifecycle from `pending` to `confirmed`, `shipping`, and `completed`.
- Image upload support for product media.
- Server-rendered UI built with Django templates, CSS, and JavaScript.
- Notification endpoint for recent orders in the dashboard.

## Project Structure

- `accounts/`: custom authentication, registration, and user model
- `products/`: categories, brands, and product catalog
- `cart/`: cart persistence and quantity management
- `orders/`: order and order item domain models
- `core/`: storefront pages, search, checkout, and shared logic
- `dashboard/`: staff-facing management pages
- `config/`: project settings and root routing

## Tech Stack

- Python
- Django 6
- PostgreSQL
- HTML, CSS, JavaScript
- Pillow for image handling

## Local Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install Django Pillow psycopg[binary]
```

4. Update the `DATABASES` configuration in `config/settings.py` to match your local PostgreSQL setup.
5. Run migrations:

```bash
python manage.py migrate
```

6. Create an admin account if needed:

```bash
python manage.py createsuperuser
```

7. Start the development server:

```bash
python manage.py runserver
```

## What I Would Improve Next

- Move secrets and database credentials out of source code into environment variables.
- Add automated tests for checkout, permissions, and dashboard workflows.
- Add deployment and CI/CD configuration.
- Expand analytics, promotions, and inventory reporting features.

## Closing Note

This project is intended to show practical full-stack backend-focused engineering skills: building usable product flows, modeling business data, and handling operational edge cases in an e-commerce setting.
