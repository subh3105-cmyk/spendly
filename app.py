from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database.db import init_db, seed_db, create_user, get_user_by_email
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "spendly_secret_key" # Required for flashing messages

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def guest_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" in session:
            flash("You are already logged in.", "info")
            return redirect(url_for("profile"))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/register", methods=["GET", "POST"])
@guest_only
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if get_user_by_email(email):
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)
        create_user(name, email, hashed_password)

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@guest_only
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please provide both email and password.", "error")
            return render_template("login.html")

        user = get_user_by_email(email)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))
        else:
            flash("Invalid email or password.", "error")
            return render_template("login.html")

    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
@login_required
def profile():
    # Hardcoded data for Step 4 UI validation
    user = {
        "name": "Raj Yadav",
        "email": "subh3105@gmail.com",
        "member_since": "January 2024",
        "initials": "RY"
    }

    stats = {
        "total_spent": "₹12,450.00",
        "transaction_count": 42,
        "top_category": "Food & Dining"
    }

    transactions = [
        {"date": "2024-09-20", "description": "Grocery Store", "category": "Groceries", "amount": "₹1,200.00"},
        {"date": "2024-09-18", "description": "Petrol Pump", "category": "Transport", "amount": "₹2,500.00"},
        {"date": "2024-09-15", "description": "Netflix Subscription", "category": "Entertainment", "amount": "₹499.00"},
        {"date": "2024-09-12", "description": "Dinner at Taj", "category": "Food & Dining", "amount": "₹3,200.00"},
        {"date": "2024-09-10", "description": "Electricity Bill", "category": "Utilities", "amount": "₹1,800.00"},
    ]

    categories = [
        {"name": "Food & Dining", "amount": "₹4,500.00", "percentage": 36},
        {"name": "Transport", "amount": "₹3,000.00", "percentage": 24},
        {"name": "Groceries", "amount": "₹2,500.00", "percentage": 20},
        {"name": "Utilities", "amount": "₹1,500.00", "percentage": 12},
        {"name": "Entertainment", "amount": "₹950.00", "percentage": 8},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
