# SpendSmart 💰# 💰 SpendSmart – Smart Way to Manage Expenses



**Smart Way to Manage Expenses** - A modern Flask-based personal expense tracking application with beautiful UI, smart analytics, and budget management.**SpendSmart** is a simple, beginner-friendly budget-tracking web application built with Python and Flask. It helps users record daily expenses, organize spending by category, compare spending against budgets, and visualize patterns with charts.



![Python](https://img.shields.io/badge/python-3.8+-blue.svg)---

![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)

![License](https://img.shields.io/badge/license-MIT-blue.svg)## 🎯 Key Features



## ✨ Features- Add Expenses — enter amount, category, description, and date.

- Categorize Spending — group expenses under categories like Food, Rent, Shopping.

### 🔐 User Authentication- Track Budget vs Spent — set monthly budgets and see remaining balance per category.

- Secure signup/login with password hashing- Visual Dashboard — interactive charts (Chart.js) showing expense distribution.

- Password visibility toggle with eye icon- Monthly Summary — filter and view totals for a selected month.

- Email validation- Edit / Delete — correct or remove previously recorded expenses.

- Change password functionality

- Per-user data isolation---

    

### 💳 Expense Management- Add user authentication (login/register)

- Add, edit, and delete expenses- Allow filtering by month and exporting reports (CSV/PDF)

- Categorize expenses (Food, Rent, Transport, etc.)- Notifications when a category exceeds its monthly budget

- Date tracking for all expenses- Containerize with Docker

- Real-time expense history

---

### 📊 Smart Dashboard

- **Monthly Analytics**: Automatically scoped to current monthIf you want, I can also:

- **Burn Rate Analysis**: Compare daily budget vs actual spending- Convert this README into a GitHub-ready README with badges and screenshots.

- **End-of-Month Projection**: Forecast spending based on current pace- Generate the Flask skeleton (app.py, templates, static files, tests) in this repo now.

- **Risk Detection**: Flags categories likely to exceed budget- Add a Dockerfile and GitHub Actions workflow to build and test the app.

- **Top 3 Categories**: Quick view of highest spending areas

- **Interactive Doughnut Chart**: Visual breakdown with Chart.jsWhich one should I do next?

### 🏷️ Category Management
- Create custom categories with budgets
- Edit category names and budgets
- Delete categories (cascades to related expenses)
- Track expense count per category
- Budget vs actual spending comparison

### 🇮🇳 Indian Rupee Support
- All amounts displayed in ₹ (INR)
- Proper thousand separator formatting
- Currency filter throughout the app

### 🎨 Modern UI/UX
- Clean, responsive Bootstrap 5 design
- Subtle pastel gradient background
- Card-based layout with shadows
- Bootstrap Icons integration
- Mobile-friendly interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/spendsmart.git
cd spendsmart
```

2. **Create virtual environment**
```bash
python -m venv .venv
```

3. **Activate virtual environment**

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
.venv\Scripts\activate.bat
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
```
http://127.0.0.1:5000
```

## 📁 Project Structure

```
spendsmart/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── view_data.py               # Database viewer script
├── static/
│   ├── style.css              # Custom styles with gradient theme
│   └── script.js              # Client-side JS (password toggle, validation)
└── templates/
    ├── layout.html            # Base template with navbar
    ├── index.html             # Home/overview page
    ├── login.html             # Login page
    ├── signup.html            # Signup page
    ├── dashboard.html         # Analytics dashboard
    ├── add_expense.html       # Add expense form
    ├── edit_expense.html      # Edit expense form
    ├── view_expenses.html     # Expense history table
    ├── categories.html        # Category management
    ├── edit_category.html     # Edit category form
    └── change_password.html   # Change password form
```

## 🛠️ Technology Stack

- **Backend**: Flask 3.0+
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with password hashing
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Charts**: Chart.js
- **Python Libraries**:
  - Flask-SQLAlchemy (database ORM)
  - Flask-Login (session management)
  - Werkzeug (password security)

## 📊 Database Schema

### User
- `id`: Primary key
- `email`: Unique email address
- `password_hash`: Hashed password
- `created_at`: Timestamp

### Category
- `id`: Primary key
- `name`: Category name
- `budget`: Monthly budget amount
- `user_id`: Foreign key to User

### Expense
- `id`: Primary key
- `description`: Expense description
- `amount`: Expense amount
- `date`: Transaction date
- `category_id`: Foreign key to Category
- `user_id`: Foreign key to User

## 🔧 Configuration

Edit `app.py` to customize:

```python
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spendsmart.db'
```

## 📱 Usage

1. **Sign Up**: Create a new account with email and password
2. **Add Categories**: Set up spending categories with monthly budgets
3. **Track Expenses**: Add daily expenses to categories
4. **View Dashboard**: Monitor spending patterns and projections
5. **Manage Data**: Edit or delete expenses and categories as needed

## 🎯 Key Algorithms

### Burn Rate Calculation
```python
daily_budget = total_budget / days_in_month
daily_spend_avg = total_spent / days_passed
projected_eom_spend = daily_spend_avg * days_in_month
burn_variance = daily_spend_avg - daily_budget
```

### Risk Detection
Categories flagged as "at risk" if spending exceeds 110% of expected pace:
```python
expected_to_date = (budget * days_passed) / days_in_month
risk = spent > expected_to_date * 1.10
```

## 🗂️ View Database

Use the included script to inspect your data:
```bash
python view_data.py
```

Shows all users, categories, expenses, and totals.

## 🔒 Security Features

- Passwords hashed with `werkzeug.security`
- CSRF protection via Flask
- SQL injection prevention with SQLAlchemy ORM
- Per-user data isolation with `@login_required`
- Session-based authentication

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

MIT License - feel free to use this project for learning or personal use.

## 👤 Author

Created with ❤️ for smart expense management

## 🙏 Acknowledgments

- Bootstrap team for the UI framework
- Flask community for excellent documentation
- Chart.js for beautiful visualizations

---

**Happy Budgeting! 💰✨**
