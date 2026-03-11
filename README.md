# Personal Finance API

A RESTful API for managing personal finances. Users can track income and expenditure transactions, organize them into categories, set monthly budgets, and get spending summaries — all behind JWT authentication.

---

## Features

- User registration and login with JWT authentication
- Create and manage spending/income categories
- Set monthly budgets per category
- Log income and expenditure transactions
- Automatic over-budget detection on every transaction
- Monthly spending summary grouped by category

---

## Tech Stack

| Layer          | Technology                   |
| -------------- | ---------------------------- |
| Framework      | Django 6.0.2                 |
| API            | Django REST Framework 3.16.1 |
| Authentication | SimpleJWT 5.5.1              |
| Database       | SQLite (development)         |
| Testing        | pytest + pytest-django       |

---

## Project Structure

```
personal-finance-backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/
│   ├── models.py         # Category, Budget, Transaction
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests/
│       ├── test_auth.py
│       ├── test_categories.py
│       ├── test_budgets.py
│       ├── test_transactions.py
│       └── test_category_summary.py
├── requirements.txt
├── pytest.ini
└── manage.py
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip
- virtualenv (recommended)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/personal-finance-backend.git
cd personal-finance-backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Run the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## Environment Variables

Before running in production, replace the following in `settings.py` or move them to a `.env` file:

| Variable        | Description                                     |
| --------------- | ----------------------------------------------- |
| `SECRET_KEY`    | Django secret key — keep this private           |
| `DEBUG`         | Set to `False` in production                    |
| `ALLOWED_HOSTS` | Add your domain or server IP                    |
| `DATABASES`     | Switch from SQLite to PostgreSQL for production |

---

## API Endpoints

All endpoints are prefixed with `/api/`.  
Protected endpoints require a JWT access token in the header:

```
Authorization: Bearer <access_token>
```

### Auth

| Method | Endpoint              | Description                  | Auth Required |
| ------ | --------------------- | ---------------------------- | ------------- |
| POST   | `/api/auth/register/` | Register a new user          | No            |
| POST   | `/api/auth/login/`    | Login and receive JWT tokens | No            |
| GET    | `/api/auth/profile/`  | Get current user's profile   | Yes           |

### Categories

| Method | Endpoint                | Description            | Auth Required |
| ------ | ----------------------- | ---------------------- | ------------- |
| GET    | `/api/categories/`      | List user's categories | Yes           |
| POST   | `/api/categories/`      | Create a new category  | Yes           |
| GET    | `/api/categories/{id}/` | Retrieve a category    | Yes           |
| PUT    | `/api/categories/{id}/` | Update a category      | Yes           |
| DELETE | `/api/categories/{id}/` | Delete a category      | Yes           |

### Budgets

| Method | Endpoint             | Description                               | Auth Required |
| ------ | -------------------- | ----------------------------------------- | ------------- |
| GET    | `/api/budgets/`      | List budgets with spent/remaining amounts | Yes           |
| POST   | `/api/budgets/`      | Create a budget for a category            | Yes           |
| GET    | `/api/budgets/{id}/` | Retrieve a budget                         | Yes           |
| PUT    | `/api/budgets/{id}/` | Update a budget                           | Yes           |
| DELETE | `/api/budgets/{id}/` | Delete a budget                           | Yes           |

### Transactions

| Method | Endpoint                  | Description              | Auth Required |
| ------ | ------------------------- | ------------------------ | ------------- |
| GET    | `/api/transactions/`      | List user's transactions | Yes           |
| POST   | `/api/transactions/`      | Create a transaction     | Yes           |
| GET    | `/api/transactions/{id}/` | Retrieve a transaction   | Yes           |
| PUT    | `/api/transactions/{id}/` | Update a transaction     | Yes           |
| DELETE | `/api/transactions/{id}/` | Delete a transaction     | Yes           |

> When creating an expenditure transaction, the response includes `is_over_budget` and `remaining_budget` fields automatically.

### Summary

| Method | Endpoint                 | Description                                 | Auth Required |
| ------ | ------------------------ | ------------------------------------------- | ------------- |
| GET    | `/api/summary/category/` | Monthly spending totals grouped by category | Yes           |

---

## Example Requests

### Register

```json
POST /api/auth/register/
{
    "username": "john",
    "email": "john@example.com",
    "password": "strongpassword123"
}
```

### Create a Transaction

```json
POST /api/transactions/
{
    "category": 1,
    "amount": "50.00",
    "type": "expenditure",
    "description": "Lunch"
}
```

### Response (with budget info)

```json
{
  "id": 3,
  "category": 1,
  "amount": "50.00",
  "type": "expenditure",
  "description": "Lunch",
  "date": "2026-03-04",
  "is_over_budget": false,
  "remaining_budget": "50.00"
}
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run a specific test file
pytest api/tests/test_budgets.py

# Run with verbose output
pytest -v
```

---

## Known Issues / Roadmap

- [ ] `Transaction.date` uses `auto_now_add=True` — cannot be set manually, which affects some tests. Planned fix: switch to `default=date.today` to allow backdating.
- [ ] Budget period is currently limited to `monthly` only. Weekly and yearly periods planned.
- [ ] No pagination on list endpoints yet.
- [ ] Switch to PostgreSQL for production deployment.

---

## License

This project is for personal/educational use.
