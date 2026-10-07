from database.db import get_db
from datetime import datetime

def delete_expense_by_id(expense_id, user_id):
    """
    Deletes a specific expense record if it belongs to the given user.
    """
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0

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

def _apply_date_filter(query, params, date_from, date_to):
    """
    Helper to append date BETWEEN clause and params if date bounds are provided.
    """
    if date_from and date_to:
        query += " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])
    return query, params

def get_summary_stats(user_id, date_from=None, date_to=None):
    """
    Calculates total spent, transaction count, and identifies the top category.
    """
    with get_db() as conn:
        # Total and Count
        query = "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?"
        params = [user_id]
        query, params = _apply_date_filter(query, params, date_from, date_to)

        stats = conn.execute(query, tuple(params)).fetchone()

        total_spent = stats["total"] or 0.0
        transaction_count = stats["count"] or 0

        # Top Category
        top_cat_query = "SELECT category FROM expenses WHERE user_id = ?"
        top_params = [user_id]
        top_cat_query, top_params = _apply_date_filter(top_cat_query, top_params, date_from, date_to)

        top_cat_query += " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1"

        top_cat_row = conn.execute(top_cat_query, tuple(top_params)).fetchone()
        top_category = top_cat_row["category"] if top_cat_row else "—"

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }

def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    """
    Fetches the most recent transactions for a user.
    """
    with get_db() as conn:
        query = "SELECT id, date, description, category, amount FROM expenses WHERE user_id = ?"
        params = [user_id]
        query, params = _apply_date_filter(query, params, date_from, date_to)

        query += " ORDER BY date DESC, created_at DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(row) for row in rows]

def get_expense_by_id(expense_id):
    """
    Fetches a single expense by its ID.
    """
    with get_db() as conn:
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        return dict(row) if row else None

def update_expense(expense_id, amount, category, date, description):
    """
    Updates an existing expense's details.
    """
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ?",
            (amount, category, date, description, expense_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def get_category_breakdown(user_id, date_from=None, date_to=None):
    """
    Fetches total spend per category and calculates percentages.
    """
    with get_db() as conn:
        query = "SELECT category as name, SUM(amount) as amount FROM expenses WHERE user_id = ?"
        params = [user_id]
        query, params = _apply_date_filter(query, params, date_from, date_to)

        query += " GROUP BY category ORDER BY amount DESC"

        rows = conn.execute(query, tuple(params)).fetchall()

        if not rows:
            return []

        grand_total = sum(row["amount"] for row in rows)
        if grand_total == 0:
            return [{"name": row["name"], "amount": 0, "pct": 0} for row in rows]

        breakdown = []
        sum_pct = 0
        for i, row in enumerate(rows):
            pct = round((row["amount"] / grand_total) * 100)
            if i == len(rows) - 1:
                pct = 100 - sum_pct
            breakdown.append({"name": row["name"], "amount": row["amount"], "pct": pct})
            sum_pct += pct

        return breakdown
