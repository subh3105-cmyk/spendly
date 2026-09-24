import sqlite3
import random
from datetime import datetime, timedelta
from database.db import get_db

def print_usage():
    print("\n**Missing Arguments**")
    print("Usage: `/seed-expenses <user_id> <count> <months>`")
    print("\n**Argument Hints:**")
    print("- `<user_id>`: The numeric ID of the user to seed expenses for.")
    print("- `<count>`: Total number of random expenses to generate.")
    print("- `<months>`: Time window in months to spread expenses over.")
    print("\n**Example:** `/seed-expenses 1 50 6`\n")

def seed_expenses(user_id_str, count_str, months_str):
    # Step 1: Parse arguments
    try:
        user_id = int(user_id_str)
        count = int(count_str)
        months = int(months_str)
    except (ValueError, TypeError):
        print_usage()
        return

    try:
        conn = get_db()
        cursor = conn.cursor()

        # Step 2: Verify user exists
        user = cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            print(f"No user found with id {user_id}.")
            return

        # Step 3: Generate expenses
        categories = {
            "Food": {"range": (50, 800), "weight": 30, "desc": ["Lunch at Cafe", "Grocery Shopping", "Dinner at Restaurant", "Coffee/Tea", "Street Food"]},
            "Transport": {"range": (20, 500), "weight": 20, "desc": ["Auto Rickshaw", "Uber/Ola", "Metro Fare", "Petrol Fill", "Bus Ticket"]},
            "Bills": {"range": (200, 3000), "weight": 15, "desc": ["Electricity Bill", "Water Bill", "Internet Recharge", "Mobile Bill", "Rent"]},
            "Health": {"range": (100, 2000), "weight": 5, "desc": ["Pharmacy", "Doctor Consultation", "Medical Test", "Health Supplement"]},
            "Entertainment": {"range": (100, 1500), "weight": 10, "desc": ["Movie Ticket", "Netflix Subscription", "Gaming Zone", "Concert Ticket"]},
            "Shopping": {"range": (200, 5000), "weight": 15, "desc": ["New Clothes", "Electronics", "Footwear", "Home Decor"]},
            "Other": {"range": (50, 1000), "weight": 5, "desc": ["Gift Wrap", "Stationery", "Donation", "Miscellaneous"]},
        }

        cat_list = list(categories.keys())
        weights = [categories[c]["weight"] for c in cat_list]

        expenses_to_insert = []
        start_date = datetime.now() - timedelta(days=months * 30)

        for _ in range(count):
            cat = random.choices(cat_list, weights=weights)[0]
            amount = round(random.uniform(*categories[cat]["range"]), 2)
            description = random.choice(categories[cat]["desc"])

            # Random date within the window
            random_days = random.randint(0, months * 30)
            date_obj = start_date + timedelta(days=random_days)
            date_str = date_obj.strftime('%Y-%m-%d')

            expenses_to_insert.append((user_id, amount, cat, date_str, description))

        # Insert in a single transaction
        try:
            cursor.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses_to_insert
            )
            conn.commit()

            # Step 4: Confirm
            print(f"Successfully inserted {len(expenses_to_insert)} expenses.")

            # Calculate date range
            dates = [e[3] for e in expenses_to_insert]
            print(f"Date range: {min(dates)} to {max(dates)}")

            print("\nSample records:")
            sample = random.sample(expenses_to_insert, min(5, len(expenses_to_insert)))
            for s in sample:
                print(f"₹{s[1]} | {s[2]} | {s[3]} | {s[4]}")

        except Exception as e:
            conn.rollback()
            print(f"Transaction failed, rolled back: {e}")
        finally:
            conn.close()

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print_usage()
    else:
        seed_expenses(sys.argv[1], sys.argv[2], sys.argv[3])
