# Spec: Login and Logout

## Overview
This feature enables users to authenticate into the Spendly application using their registered email and password. Once authenticated, the application will maintain a session for the user, allowing them to access protected routes and eventually manage their expenses. A logout functionality is also provided to terminate the session securely.

## Depends on
- 01-database-setup
- 02-registration

## Routes
- `GET /login` — Display the login form — public
- `POST /login` — Authenticate user and create session — public
- `GET /logout` — Terminate user session and redirect to landing — logged-in

## Database changes
No database changes.

## Templates
- **Modify:** `login.html` — Update to include a proper form and handle flash messages.
- **Modify:** `base.html` — Add conditional navigation links (e.g., show "Logout" and "Profile" when logged in, show "Login" and "Register" when logged out).

## Files to change
- `app.py` — Implement login and logout logic, session management, and route updates.
- `templates/login.html` — Update the login form.
- `templates/base.html` — Update navigation bar based on session state.

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
- Use Flask `session` for managing the logged-in state.

## Definition of done
- [ ] User can log in with valid credentials and is redirected to the profile page (or landing).
- [ ] User sees an error message when attempting to log in with an incorrect password.
- [ ] User sees an error message when attempting to log in with an unregistered email.
- [ ] User can log out, which clears the session and redirects them to the landing page.
- [ ] Navigation menu updates dynamically based on whether the user is logged in or out.
