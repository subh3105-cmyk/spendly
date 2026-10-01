import pytest
from database.db import get_db, init_db, seed_db
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown
)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Use a temporary database for testing if possible,
    # but here we follow the project structure.
    init_db()
    seed_db()

def test_get_user_by_id():
    # Seed user is demo@spendly.com
    with get_db() as conn:
        user = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
        user_id = user["id"]

    user_data = get_user_by_id(user_id)
    assert user_data is not None
    assert user_data["name"] == "Demo User"
    assert user_data["email"] == "demo@spendly.com"
    assert "2026" in user_data["member_since"] # Seeded data date

    assert get_user_by_id(9999) is None

def test_get_summary_stats():
    with get_db() as conn:
        user = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
        user_id = user["id"]

    stats = get_summary_stats(user_id)
    # Seed data: 8 expenses, sum is 346.24 (approximately, based on seed_db logic)
    assert stats["transaction_count"] == 8
    assert stats["total_spent"] > 0
    assert stats["top_category"] == "Bills" # Electricity bill is 120.00, highest in seed

    # Test user with no expenses
    with get_db() as conn:
        conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                     ("Empty User", "empty@test.com", "hash"))
        empty_user = conn.execute("SELECT id FROM users WHERE email = ?", ("empty@test.com",)).fetchone()
        empty_id = empty_user["id"]

    empty_stats = get_summary_stats(empty_id)
    assert empty_stats["total_spent"] == 0
    assert empty_stats["transaction_count"] == 0
    assert empty_stats["top_category"] == "—"

def test_get_recent_transactions():
    with get_db() as conn:
        user = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
        user_id = user["id"]

    txs = get_recent_transactions(user_id)
    assert len(txs) == 8
    assert "amount" in txs[0]
    assert "date" in txs[0]

    assert get_recent_transactions(9999) == []

def test_get_category_breakdown():
    with get_db() as conn:
        user = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
        user_id = user["id"]

    breakdown = get_category_breakdown(user_id)
    assert len(breakdown) > 0

    # Sum of percentages should be exactly 100
    total_pct = sum(item["pct"] for item in breakdown)
    assert total_pct == 100

    # Test user with no expenses
    with get_db() as conn:
        conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                     ("Empty User 2", "empty2@test.com", "hash"))
        empty_user = conn.execute("SELECT id FROM users WHERE email = ?", ("empty2@test.com",)).fetchone()
        empty_id = empty_user["id"]

    assert get_category_breakdown(empty_id) == []
