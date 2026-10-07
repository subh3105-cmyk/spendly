# Spec: Delete Expense

## Overview
This feature allows users to remove unwanted or incorrect expense records from their profile. It provides a way to maintain a clean and accurate financial history by enabling the deletion of specific transactions.

## Depends on
- 05-profile-backend-routes (Profile page and basic transaction listing)
- 08-edit-expense (Expense identification by ID)

## Routes
- `POST /expenses/<int:id>/delete` — Deletes a specific expense record — logged-in

## Database changes
No database changes. The existing `expenses` table supports deletion.

## Templates
- **Modify:** `templates/profile.html` — Add a delete button/link for each transaction in the recent transactions list.

## Files to change
- `app.py` — Implement the `delete_expense` route.
- `database/queries.py` — Add a `delete_expense_by_id` function.
- `templates/profile.html` — Add delete UI.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Ensure the user owning the expense is the one requesting deletion (authorization check).

## Definition of done
- [ ] A "Delete" button appears next to each expense on the profile page.
- [ ] Clicking the delete button removes the expense from the database.
- [ ] A success message "Expense deleted successfully!" is flashed upon deletion.
- [ ] A user cannot delete another user's expense by manually guessing the ID in the URL.
- [ ] The profile page refreshes and reflects the removal of the expense.
