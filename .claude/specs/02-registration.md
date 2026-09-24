# Spec: Registration

## Overview
This feature implements the user registration system for Spendly. It allows new users to create an account by providing their name, email, and password, enabling them to start tracking their expenses privately. This is a foundational step for the Spendly roadmap, moving from a static landing experience to a personalized application.

## Depends on
- Step 1: Database setup (Complete)

## Routes
- `GET /register` — Display the registration form — public
- `POST /register` — Handle form submission and create user account — public

## Database changes
No database changes. The `users` table already exists in `database/db.py` with required columns: `name`, `email`, and `password_hash`.

## Templates
- **Create:** `templates/register.html` (already exists as placeholder, will be fully implemented)
- **Modify:** `templates/base.html` (ensure navigation links are correct)

## Files to change
- `app.py`: Implement `POST /register` logic and update `register` route.
- `database/db.py`: Add a helper function to create a user and check for existing emails.

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

## Definition of done
- [ ] Navigating to `/register` displays a form with Name, Email, and Password fields.
- [ ] Submitting the form with valid data redirects the user to the login page with a success message.
- [ ] Submitting the form with an email that already exists displays an error message.
- [ ] Submitting the form with missing fields displays appropriate validation errors.
- [ ] Newly registered users are correctly stored in the `users` table with hashed passwords.
