# Custom Commands Reference

## /seed-user
Creates a single dummy user in the database.

## /seed-expenses
Seeds realistic dummy expenses for a specific user.

**Usage:** `/seed-expenses <user_id> <count> <months>`

**Arguments:**
- `<user_id>`: The numeric ID of the user to seed expenses for.
- `<count>`: Total number of expenses to generate.
- `<months>`: The number of past months to spread the expenses across.

**Example:** `/seed-expenses 1 50 6`

**Behavior:**
- Verifies user existence before proceeding.
- Uses realistic Indian descriptions and amounts (₹).
- Inserts all records in a single transaction.
- Prints a summary and a sample of 5 records upon completion.
