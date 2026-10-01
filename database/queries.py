from database.db import get_db
from datetime import datetime

def get_user_by_id(user_id):
    """
    Fetches user details by ID and formats the member since date.
    """
    with get_db() as conn:
        user = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if user:
            # Format created_at (ISO string) to "Month YYYY"
            dt = datetime.fromisoformat(user["created_at"])
            return {
                "name": user["name"],
                "email": user["email"],
                "member_since": dt.strftime("%B %Y"),
                "initials": "".join([n[0].upper() for n in user["name"].split()])
            }
        return None

def get_summary_stats(user_id):
    """
    Calculates total spent, transaction count, and identifies the top category.
    """
    with get_db() as conn:
        # Total and Count
        stats = conn.execute(
            "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        total_spent = stats["total"] or 0.0
        transaction_count = stats["count"] or 0

        # Top Category
        top_cat_row = conn.execute(
            """
            SELECT category FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
            LIMIT 1
            """,
            (user_id,)
        ).fetchone()

        top_category = top_cat_row["category"] if top_cat_row else "—"

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }

def get_recent_transactions(user_id, limit=10):
    """
    Fetches the most recent transactions for a user.
    """
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT date, description, category, amount
            FROM expenses
            WHERE user_id = ?
            ORDER BY date DESC, created_at DESC
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()

        return [dict(row) for row in rows]

def get_category_breakdown(user_id):
    """
    Fetches total spend per category and calculates percentages.
    """
    with get_db() as conn:
        # Get totals per category
        rows = conn.execute(
            """
            SELECT category as name, SUM(amount) as amount
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY amount DESC
            """,
            (user_id,)
        ).fetchall()

        if not rows:
            return []

        # Calculate total for percentages
        grand_total = sum(row["amount"] for row in rows)
        if grand_total == 0:
            return [{"name": row["name"], "amount": 0, "pct": 0} for row in rows]

        breakdown = []
        sum_pct = 0

        for i, row in enumerate(rows):
            pct = round((row["amount"] / grand_total) * 100)
            # On the last item, adjust to ensure sum is exactly 100
            if i == len(rows) - 1:
                pct = 100 - sum_pct

            breakdown.append({
                "name": row["name"],
                "amount": row["amount"],
                "pct": pct
            })
            sum_pct += pct

        return breakdown
