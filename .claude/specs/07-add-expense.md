# Spec: Add Expense

## Overview
This feature allows logged-in users to record new expenses. It provides a form to input the amount, category, date, and an optional description, which are then stored in the database linked to the current user. This is a core functionality of Spendly, enabling users to track their spending in real-time.

## Depends on
- 03-login-logout (User must be authenticated)
- 05-profile-backend-routes (Existing DB structure for expenses)

## Routes
- `GET /expenses/add` — Render the add expense form — logged-in
- `POST /expenses/add` — Process form submission and save expense to DB — logged-in

## Database changes
No database changes. The `expenses` table already exists with the required columns: `user_id`, `amount`, `category`, `date`, and `description`.

## Templates
- **Create:** `templates/add_expense.html` — Form for entering expense details.
- **Modify:** `templates/base.html` — Add a link to the "Add Expense" page in the navigation/header.

## Files to change
- `app.py` — Implement the `GET` and `POST` handlers for `/expenses/add`.
- `templates/base.html` — Add navigation link.

## Files to create
- `templates/add_expense.html` — The input form template.
- `database/queries.py` (or `database/db.py`) — Add a helper function `add_expense(user_id, amount, category, date, description)` to insert the record.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that `amount` is a positive number.
- Validate that `date` is in a valid format.

## Definition of done
- [ ] User can navigate to `/expenses/add` while logged in.
- [ ] Unauthenticated users are redirected to login when accessing `/expenses/add`.
- [ ] Submitting the form with valid data creates a record in the `expenses` table.
- [ ] New expense appears in the "Recent Transactions" list on the profile page.
- [ ] Form displays an error message if required fields (amount, category, date) are missing.
- [ ] Form displays an error message if the amount is not a valid number.
