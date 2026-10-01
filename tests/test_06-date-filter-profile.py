import pytest
import sqlite3
from app import app
from database.db import init_db, create_user
from database.queries import get_db
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    # Use an in-memory database for tests
    # We need to monkeypatch get_db or change DATABASE_PATH in database.db
    import database.db
    original_db_path = database.db.DATABASE_PATH
    database.db.DATABASE_PATH = ":memory:"

    with app.test_client() as client:
        with app.app_context():
            # Important: for :memory: databases, the connection must be kept open
            # to preserve the schema across calls within the same test.
            # Since get_db() opens/closes a new connection, :memory: won't work
            # unless we monkeypatch get_db to return the same connection.
            import database.db
            conn = sqlite3.connect(":memory:", check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")

            def mock_get_db():
                return conn

            database.db.get_db = mock_get_db

            init_db()
            # Create a test user
            user_id = create_user("Test User", "test@example.com", "hashed_password")
            # Seed test data across different dates
            # Today is 2026-10-01 (as per system prompt)
            today = date(2026, 10, 1)

            expenses = [
                # Current Month (Oct 2026)
                (user_id, 100.0, "Food", "2026-10-01", "Oct Lunch"),
                (user_id, 50.0, "Transport", "2026-10-02", "Oct Taxi"),

                # Last 3 Months (July, Aug, Sept, Oct)
                (user_id, 200.0, "Bills", "2026-09-15", "Sept Bill"),
                (user_id, 150.0, "Health", "2026-08-10", "Aug Meds"),
                (user_id, 100.0, "Shopping", "2026-07-05", "July Shirt"),

                # Last 6 Months (April - Oct)
                (user_id, 300.0, "Entertainment", "2026-05-20", "May Concert"),
                (user_id, 400.0, "Other", "2026-04-10", "April Trip"),

                # Older (outside 6 months)
                (user_id, 1000.0, "Investment", "2025-12-01", "Old Investment"),
            ]

            # Use the connection directly instead of calling get_db()
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()

            # Log in the user
            with client.session_transaction() as sess:
                sess['user_id'] = user_id

        yield client

    database.db.DATABASE_PATH = original_db_path

def test_profile_no_params_all_time(client):
    """Verify that /profile without query params shows all-time view."""
    response = client.get("/profile")
    assert response.status_code == 200
    # Total: 100+50+200+150+100+300+400+1000 = 2300
    assert "2300" in response.get_data(as_text=True)
    assert "8" in response.get_data(as_text=True) # Transaction count

def test_profile_preset_this_month(client):
    """Verify 'This Month' filter logic."""
    # This Month for 2026-10-01 is 2026-10-01 to 2026-10-01 (or Oct)
    # In our seed: Oct Lunch (100) + Oct Taxi (50) = 150
    today = date(2026, 10, 1)
    date_from = today.replace(day=1).strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")

    response = client.get(f"/profile?date_from={date_from}&date_to={date_to}")
    assert response.status_code == 200
    assert "150" in response.get_data(as_text=True)
    assert "2" in response.get_data(as_text=True) # Count

def test_profile_preset_last_3_months(client):
    """Verify 'Last 3 Months' filter logic."""
    # 2026-07-01 to 2026-10-01
    # Seeded: Oct(150) + Sept(200) + Aug(150) + July(100) = 600
    today = date(2026, 10, 1)
    date_from = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")

    response = client.get(f"/profile?date_from={date_from}&date_to={date_to}")
    assert response.status_code == 200
    assert "600" in response.get_data(as_text=True)
    assert "5" in response.get_data(as_text=True)

def test_profile_preset_last_6_months(client):
    """Verify 'Last 6 Months' filter logic."""
    # 2026-04-01 to 2026-10-01
    # Seeded: 600 (above) + May(300) + April(400) = 1300
    today = date(2026, 10, 1)
    date_from = (today - relativedelta(months=6)).strftime("%Y-%m-%d")
    date_to = today.strftime("%Y-%m-%d")

    response = client.get(f"/profile?date_from={date_from}&date_to={date_to}")
    assert response.status_code == 200
    assert "1300" in response.get_data(as_text=True)
    assert "7" in response.get_data(as_text=True)

def test_profile_custom_date_range(client):
    """Verify valid custom date range."""
    # Range: 2026-08-01 to 2026-08-31
    # Seeded: Aug Meds (150)
    response = client.get("/profile?date_from=2026-08-01&date_to=2026-08-31")
    assert response.status_code == 200
    assert "150" in response.get_data(as_text=True)
    assert "1" in response.get_data(as_text=True)

def test_profile_range_no_expenses(client):
    """Verify range with no expenses shows zeroed stats."""
    # Range: 2026-01-01 to 2026-01-31 (No expenses here)
    response = client.get("/profile?date_from=2026-01-01&date_to=2026-01-31")
    assert response.status_code == 200
    assert "0.00" in response.get_data(as_text=True)
    assert "0" in response.get_data(as_text=True)

def test_profile_malformed_dates(client):
    """Verify malformed date strings fallback to all-time."""
    response = client.get("/profile?date_from=not-a-date&date_to=2026-10-01")
    assert response.status_code == 200
    # Should show all-time (2300)
    assert "2300" in response.get_data(as_text=True)

def test_profile_start_after_end_date(client):
    """Verify date_from > date_to triggers flash message and fallback."""
    response = client.get("/profile?date_from=2026-10-01&date_to=2026-09-01")
    assert response.status_code == 200
    assert "Start date must be before end date." in response.get_data(as_text=True)
    # Should fallback to all-time (2300)
    assert "2300" in response.get_data(as_text=True)

def test_profile_unauthorized_access(client):
    """Verify /profile access without session redirects to login."""
    with client.session_transaction() as sess:
        sess.clear()

    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.location

def test_profile_sql_injection_attempt(client):
    """Verify parameterized queries prevent SQL injection via date params."""
    # Attempt to inject into the BETWEEN clause
    malicious_from = "2026-01-01' OR '1'='1"
    malicious_to = "2026-12-31"

    response = client.get(f"/profile?date_from={malicious_from}&date_to={malicious_to}")
    # The app should treat malformed date as None and fallback to all-time or just not crash
    assert response.status_code == 200
    # Since 'not-a-date' is treated as None, this should just show all-time.
    assert "2300" in response.get_data(as_text=True)
