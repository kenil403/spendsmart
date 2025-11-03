import sqlite3

conn = sqlite3.connect('spendsmart.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n=== SPENDSMART DATABASE ===\n")

print("--- Users ---")
users = cursor.execute("SELECT * FROM user").fetchall()
if users:
    for row in users:
        print(dict(row))
else:
    print("No users found")

print("\n--- Categories ---")
categories = cursor.execute("SELECT * FROM category").fetchall()
if categories:
    for row in categories:
        print(dict(row))
else:
    print("No categories found")

print("\n--- Expenses ---")
expenses = cursor.execute("SELECT * FROM expense").fetchall()
if expenses:
    for row in expenses:
        print(dict(row))
else:
    print("No expenses found")

print("\n--- Summary ---")
user_count = cursor.execute("SELECT COUNT(*) as count FROM user").fetchone()['count']
category_count = cursor.execute("SELECT COUNT(*) as count FROM category").fetchone()['count']
expense_count = cursor.execute("SELECT COUNT(*) as count FROM expense").fetchone()['count']
total_amount = cursor.execute("SELECT SUM(amount) as total FROM expense").fetchone()['total'] or 0

print(f"Total Users: {user_count}")
print(f"Total Categories: {category_count}")
print(f"Total Expenses: {expense_count}")
print(f"Total Amount Spent: ₹{total_amount:,.2f}")

conn.close()
