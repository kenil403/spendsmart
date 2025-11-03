from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, login_required, current_user, logout_user, UserMixin
)
from datetime import datetime, date, timedelta
import calendar
import os

app = Flask(__name__)
# Use SECRET_KEY from environment (Render auto-generates this)
app.secret_key = os.environ.get('SECRET_KEY', os.environ.get('SPENDSMART_SECRET', 'dev-secret-change-in-production'))

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'spendsmart.db')
# Support DATABASE_URL for PostgreSQL or fallback to SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + db_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    budget = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expenses = db.relationship('Expense', backref='category', lazy=True, cascade='all, delete-orphan')

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'date': self.date.isoformat(),
            'category': self.category.name if self.category else None
        }

def init_db():
    """Initialize the database (create tables). For dev, auto-rebuild if legacy schema detected."""
    from sqlalchemy import text
    # Detect legacy schema (no user table or categories without user_id)
    try:
        with db.engine.connect() as conn:
            has_user = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user'"))\
                .first() is not None
            if not has_user:
                db.drop_all()
                db.create_all()
                return
    except Exception:
        # If inspection fails, just create all
        pass
    # Default path
    db.create_all()

@login_manager.user_loader
def load_user(user_id: str):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

@app.route('/')
@login_required
def index():
    # Show categories with totals and a quick list of recent expenses
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    expenses_recent = (
        Expense.query.filter_by(user_id=current_user.id)
        .order_by(Expense.date.desc()).limit(10).all()
    )

    per_category = {}
    total_budget = 0.0
    total_spent = 0.0
    for c in categories:
        spent = sum(e.amount for e in c.expenses)
        per_category[c.name] = {'budget': c.budget or 0.0, 'spent': spent}
        total_budget += c.budget or 0.0
        total_spent += spent

    return render_template('index.html', categories=categories, per_category=per_category,
                           total_budget=total_budget, total_spent=total_spent, expenses_recent=expenses_recent)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', '0'))
        except ValueError:
            flash('Invalid amount', 'danger')
            return redirect(url_for('add_expense'))
        if amount <= 0:
            flash('Amount must be greater than zero', 'warning')
            return redirect(url_for('add_expense'))
        description = request.form.get('description', '')
        category_id = int(request.form.get('category'))
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        # Verify category belongs to current user
        cat = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
        if not cat:
            flash('Invalid category', 'danger')
            return redirect(url_for('add_expense'))
        e = Expense(description=description, amount=amount, category_id=category_id, date=date, user_id=current_user.id)
        db.session.add(e)
        db.session.commit()
        flash('Expense added', 'success')
        return redirect(url_for('index'))
    return render_template('add_expense.html', categories=categories)

@app.route('/view')
@login_required
def view_expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('view_expenses.html', expenses=expenses)

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    e = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    if request.method == 'POST':
        e.description = request.form.get('description', e.description)
        try:
            e.amount = float(request.form.get('amount', e.amount))
        except ValueError:
            flash('Invalid amount', 'danger')
            return redirect(url_for('edit_expense', expense_id=expense_id))
        e.category_id = int(request.form.get('category', e.category_id))
        date_str = request.form.get('date')
        e.date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else e.date
        db.session.commit()
        flash('Expense updated', 'success')
        return redirect(url_for('view_expenses'))
    return render_template('edit_expense.html', expense=e, categories=categories)

@app.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    e = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(e)
    db.session.commit()
    flash('Expense deleted', 'info')
    return redirect(url_for('view_expenses'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Current month bounds
    today = date.today()
    first_day = today.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    next_month = (first_day + timedelta(days=days_in_month))
    # Load user categories
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    labels = [c.name for c in categories]
    # Monthly totals per category
    values = []
    budgets = []
    for c in categories:
        monthly_spent = sum(
            e.amount for e in c.expenses
            if (e.date.date() >= first_day and e.date.date() < next_month)
        )
        values.append(monthly_spent)
        budgets.append(c.budget or 0.0)
    total_budget = sum(budgets)
    total_spent = sum(values)
    remaining = total_budget - total_spent
    days_passed = today.day
    daily_budget = (total_budget / days_in_month) if days_in_month else 0.0
    daily_spend_avg = (total_spent / days_passed) if days_passed else 0.0
    projected_eom_spend = daily_spend_avg * days_in_month
    burn_variance = daily_spend_avg - daily_budget  # >0 means overspending pace
    top_idx = max(range(len(values)), key=lambda i: values[i]) if values else None
    top_category = labels[top_idx] if top_idx is not None else None
    # Risky categories: spending pace likely to exceed budget (simple heuristic)
    risk_thresholds = []
    for i, name in enumerate(labels):
        expected_to_date = (budgets[i] * days_passed / days_in_month) if days_in_month else 0.0
        risk = values[i] > expected_to_date * 1.10  # 10% over expected pace
        risk_thresholds.append({
            'name': name,
            'spent': values[i],
            'budget': budgets[i],
            'expected_to_date': expected_to_date,
            'risk': risk
        })
    risk_categories = [r for r in risk_thresholds if r['risk']]
    # Top 3 categories by spend this month
    top3 = sorted([
        {'name': labels[i], 'spent': values[i], 'budget': budgets[i]} for i in range(len(labels))
    ], key=lambda x: x['spent'], reverse=True)[:3]
    return render_template(
        'dashboard.html',
        labels=labels, values=values, budgets=budgets,
        total_budget=total_budget, total_spent=total_spent, remaining=remaining,
        top_category=top_category,
        days_in_month=days_in_month, days_passed=days_passed,
        daily_budget=daily_budget, daily_spend_avg=daily_spend_avg,
        projected_eom_spend=projected_eom_spend, burn_variance=burn_variance,
        risk_categories=risk_categories, top3=top3
    )

# Currency formatting for INR (simple)
@app.template_filter('inr')
def inr(amount):
    try:
        return f"₹{float(amount):,.2f}"
    except Exception:
        return f"₹{amount}"

@app.route('/api/expenses')
@login_required
def api_expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return jsonify([e.to_dict() for e in expenses])

@app.route('/init_sample')
@login_required
def init_sample():
    # idempotent sample seed route for quick demo; not secured — remove in production
    if Category.query.filter_by(user_id=current_user.id).count() > 0:
        return 'Already initialized', 200
    cats = [
        Category(name='Food', budget=5000, user_id=current_user.id),
        Category(name='Rent', budget=10000, user_id=current_user.id),
        Category(name='Shopping', budget=3000, user_id=current_user.id),
        Category(name='Transport', budget=1000, user_id=current_user.id)
    ]
    db.session.add_all(cats)
    db.session.commit()
    sample_expenses = [
        Expense(description='Groceries', amount=3200, category_id=cats[0].id, user_id=current_user.id, date=datetime.utcnow()),
        Expense(description='Monthly rent', amount=10000, category_id=cats[1].id, user_id=current_user.id, date=datetime.utcnow()),
        Expense(description='Shoes', amount=1500, category_id=cats[2].id, user_id=current_user.id, date=datetime.utcnow())
    ]
    db.session.add_all(sample_expenses)
    db.session.commit()
    return 'Sample data created', 201

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate current password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('change_password'))
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters', 'warning')
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'warning')
            return redirect(url_for('change_password'))
        
        # Update password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('change_password.html')

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        try:
            budget = float(request.form.get('budget') or 0)
        except ValueError:
            budget = 0.0
        if not name:
            flash('Category name is required', 'warning')
            return redirect(url_for('categories'))
        # avoid duplicates per user
        if Category.query.filter_by(user_id=current_user.id, name=name).first():
            flash('Category already exists', 'info')
            return redirect(url_for('categories'))
        db.session.add(Category(name=name, budget=budget, user_id=current_user.id))
        db.session.commit()
        flash('Category added', 'success')
        return redirect(url_for('categories'))
    cats = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    return render_template('categories.html', categories=cats)

@app.route('/categories/<int:cat_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(cat_id: int):
    cat = Category.query.filter_by(id=cat_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        try:
            budget = float(request.form.get('budget') or 0)
        except ValueError:
            budget = 0.0
        if not name:
            flash('Category name is required', 'warning')
            return redirect(url_for('edit_category', cat_id=cat_id))
        # Prevent duplicates for this user (excluding current category)
        dup = Category.query.filter_by(user_id=current_user.id, name=name).filter(Category.id != cat.id).first()
        if dup:
            flash('Another category with this name already exists', 'danger')
            return redirect(url_for('edit_category', cat_id=cat_id))
        cat.name = name
        cat.budget = budget
        db.session.commit()
        flash('Category updated', 'success')
        return redirect(url_for('categories'))
    return render_template('edit_category.html', category=cat)

@app.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
def delete_category(cat_id: int):
    cat = Category.query.filter_by(id=cat_id, user_id=current_user.id).first_or_404()
    # Deleting category will also delete its expenses due to relationship cascade
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f'Category "{name}" deleted', 'info')
    return redirect(url_for('categories'))

# Authentication routes
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        if not email or not password:
            flash('Email and password are required', 'warning')
            return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Welcome to SpendSmart!', 'success')
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Logged in', 'success')
        next_url = request.args.get('next') or url_for('index')
        return redirect(next_url)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Initialize DB at startup (works in Flask 2 and 3)
    with app.app_context():
        init_db()
    
    # Get port from environment (Render sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    # Bind to 0.0.0.0 so Render can detect the app
    # Debug mode off in production
    app.run(host='0.0.0.0', port=port, debug=False)
