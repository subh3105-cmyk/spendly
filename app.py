from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime, date
from database.db import init_db, seed_db, create_user, get_user_by_email
from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown
from werkzeug.security import generate_password_hash, check_password_hash
from utils.date_utils import validate_date, get_profile_presets

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
    user_id = session["user_id"]
    user = get_user_by_id(user_id)

    # Date filtering logic
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    # Validate dates using utility
    validated_from = validate_date(date_from)
    validated_to = validate_date(date_to)

    if validated_from and validated_to:
        if validated_from > validated_to:
            flash("Start date must be before end date.", "error")
            validated_from = None
            validated_to = None

    # Fetch filtered data
    stats = get_summary_stats(user_id, validated_from, validated_to)
    transactions = get_recent_transactions(user_id, date_from=validated_from, date_to=validated_to)
    categories = get_category_breakdown(user_id, validated_from, validated_to)

    # Calculation for presets using utility
    presets = get_profile_presets()

    # Calculate total filtered spend for the template
    total_filtered_spend = sum(cat["amount"] for cat in categories)

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        total_filtered_spend=total_filtered_spend,
        date_from=validated_from,
        date_to=validated_to,
        presets=presets
    )


@app.route("/analytics")
@login_required
def analytics():
    return render_template("analytics.html")


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
