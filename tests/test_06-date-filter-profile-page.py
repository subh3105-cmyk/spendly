import pytest
from app import app
from database.db import init_db, create_user
from database.queries import get_summary_stats, get_recent_transactions, get_category_breakdown
from database.db import get_db
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.secret_key = "test_key"

    with app.test_client() as client:
        with app.app_context():
            init_db()
            # Create a test user
            create_user("Test User", "test@example.com", "hashed_password")
            # Manually insert session user_id for tests that need login
            with client.session_transaction() as sess:
                sess['user_id'] = 1
        yield client

def add_expense(user_id, date, amount, category, description="Test Expense"):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO expenses (user_id, date, amount, category, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, date, amount, category, description)
        )
        conn.commit()

def test_profile_auth_guard(client):
    """Ensure /profile requires login."""
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get("/profile", follow_redirects=True)
    assert b"Please log in to access this page." in response.data
    assert b"login" in response.request.path or b"login" in response.data

def test_profile_all_time_no_params(client):
    """Visiting /profile with no query params returns all expenses."""
    user_id = 1
    add_expense(user_id, "2023-01-01", 100.0, "Food")
    add_expense(user_id, "2024-01-01", 200.0, "Rent")

    response = client.get("/profile")
    assert response.status_code == 200
    # Check if both expenses are accounted for in stats
    # Since we are testing based on the spec, we verify that the returned HTML contains the totals
    # However, the spec asks to verify DB side effects for query helpers too.
    assert b"300.0" in response.data # Simplified check for ₹300.00

def test_profile_date_filter_happy_path(client):
    """Filtering with valid custom range."""
    user_id = 1
    add_expense(user_id, "2023-01-01", 100.0, "Food") # Outside
    add_expense(user_id, "2023-06-01", 200.0, "Rent") # Inside
    add_expense(user_id, "2023-06-15", 50.0, "Food")   # Inside
    add_expense(user_id, "2023-12-01", 100.0, "Gas")   # Outside

    # Filter for June 2023
    response = client.get("/profile?date_from=2023-06-01&date_to=2023-06-30")
    assert response.status_code == 200
    assert b"250.0" in response.data # 200 + 50
    assert b"Rent" in response.data
    assert b"Food" in response.data
    assert b"Gas" not in response.data

def test_profile_date_filter_no_matching_expenses(client):
    """Date range with no matching expenses."""
    user_id = 1
    add_expense(user_id, "2023-01-01", 100.0, "Food")

    response = client.get("/profile?date_from=2024-01-01&date_to=2024-01-31")
    assert response.status_code == 200
    # Spec: "user with no expenses in the selected range sees ₹0.00 total spent"
    assert b"0.00" in response.data

def test_profile_date_validation_error(client):
    """date_from > date_to (verify flash message)."""
    response = client.get("/profile?date_from=2023-12-01&date_to=2023-01-01", follow_redirects=True)
    assert b"Start date must be before end date." in response.data

def test_profile_malformed_date(client):
    """Malformed date strings should fall back to unfiltered view."""
    user_id = 1
    add_expense(user_id, "2023-01-01", 100.0, "Food")

    # Malformed date_from
    response = client.get("/profile?date_from=not-a-date&date_to=2023-12-31")
    assert response.status_code == 200
    assert b"100.0" in response.data # Should show all expenses

def test_db_query_helpers_filtering():
    """Verify that filter parameters correctly limit the data from query helpers."""
    # Use a separate connection for unit testing helpers
    with app.app_context():
        # We need a user in the DB
        create_user("Query User", "query@example.com", "pass")
        user_id = 1 # Assuming this is the first user in a fresh init_db

        # Clean expenses for this user first
        with get_db() as conn:
            conn.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
            conn.commit()

        add_expense(user_id, "2023-01-01", 100.0, "Food")
        add_expense(user_id, "2023-02-01", 200.0, "Rent")
        add_expense(user_id, "2023-03-01", 300.0, "Gas")

        # Test get_summary_stats
        stats = get_summary_stats(user_id, "2023-01-01", "2023-02-28")
        assert stats["total_spent"] == 300.0
        assert stats["transaction_count"] == 2

        # Test get_recent_transactions
        txs = get_recent_transactions(user_id, date_from="2023-01-01", date_to="2023-02-28")
        assert len(txs) == 2

        # Test get_category_breakdown
        breakdown = get_category_breakdown(user_id, "2023-01-01", "2023-02-28")
        assert len(breakdown) == 2
        categories = [item["name"] for item in breakdown]
        assert "Food" in categories
        assert "Rent" in categories
        assert "Gas" not in categories

@pytest.mark.parametrize("preset_params", [
    # These would be computed by get_profile_presets() in app.py
    # We test the behavior of the route when these types of params are passed
    ("2023-10-01", "2023-10-31"), # Mock "This Month"
    ("2023-07-01", "2023-09-30"), # Mock "Last 3 Months"
])
def test_profile_presets_logic(client, preset_params):
    """Verify that filtered requests (simulating presets) work correctly."""
    user_id = 1
    date_from, date_to = preset_params
    add_expense(user_id, date_from, 50.0, "Preset")
    add_expense(user_id, "2000-01-01", 1000.0, "Old")

    response = client.get(f"/profile?date_from={date_from}&date_to={date_to}")
    assert response.status_code == 200
    assert b"50.0" in response.data
    assert b"1000.0" not in response.data
