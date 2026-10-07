---
# Spec: Edit Expense

## Overview
This feature allows logged-in users to modify the details of an existing expense they have previously added. It ensures that users can correct mistakes in amount, category, date, or description, maintaining the accuracy of their financial tracking.

## Depends on
- 07-add-expense

## Routes
- `GET /expenses/<int:id>/edit` — Render the edit form with existing expense data — logged-in
- `POST /expenses/<int:id>/edit` — Process and save the updated expense data — logged-in

## Database changes
No database changes.

## Templates
- **Create:** `templates/edit_expense.html` (Similar to `add_expense.html` but pre-populated)
- **Modify:** No existing templates need modification.

## Files to change
- `app.py` — Implement the GET and POST handlers for the edit route.
- `database/queries.py` — Add a function to fetch a single expense by ID and a function to update an expense.

## Files to create
- `templates/edit_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- **Security:** Ensure that the user attempting to edit the expense is the owner of that expense (match `session["user_id"]` with `expenses.user_id`).

## Definition of done
- [ ] Navigating to `/expenses/<id>/edit` for an owned expense loads a form with current values.
- [ ] Navigating to `/expenses/<id>/edit` for an expense owned by another user returns a 404 or redirects with an error.
- [ ] Submitting the form updates the expense in the database.
- [ ] After updating, the user is redirected to the profile page with a success message.
- [ ] Form validation prevents saving empty required fields (amount, category, date).
---
