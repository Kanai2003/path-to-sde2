# Transaction on DB

In database management, a Transaction is a single logical unit of work that consists of one or more operations (like SQL `INSERT`, `UPDATE`, or `DELETE`). To be considered successful, every single operation within that unit must complete; if even one fails, the entire transaction is cancelled to keep your data safe.

## The ACID Properties

For a transaction to be reliable, it must follow the `ACID` rules:

- **Atomicity**: It’s `all or nothing`. Atomicity treats a series of complex steps as a single, indivisible "atom".
  If you are transferring money from Account A to Account B, the money cannot leave A without arriving at B.

- **Consistency**: The `Rule Follower`. Consistency ensures that a transaction never leaves the database in a state that violates your predefined rules. A transaction must move the database from one valid state to another, following all rules like "balance cannot be negative".

- **Isolation**: The `Private Room` Rule. Isolation is the trickiest part. It ensures that concurrent transactions (two things happening at once) don't see each other's "messy middle". If two people are using the database at the exact same time, their transactions shouldn't mess each other up.

- **Durability**: The `Concrete` Rule. Once the database says "Success," the data is saved permanently, even if the power goes out a second later.

## Key Transaction Commands

When you work in DBeaver or write code, you use these three main commands to control the flow:

1. **BEGIN (or START TRANSACTION)**: Tells the database, "Everything I do from now on is part of one single unit".

2. **COMMIT**: Saves all changes permanently. This is the "Save" button.

3. **ROLLBACK**: Undoes everything back to the BEGIN point. Use this if an error occurs.

## Real-World Example: Payment

Imagine a user buys a feature on your GitCash app. You need to do two things:

1. Deduct credits from the User table.

2. Create an entry in the Payments table.

**Without Transactions**: If the power fails after step 1 but before step 2, the user loses money, and you have no record of why.

**With Transactions**:

```SQL
BEGIN;

-- Step 1: Deduct credits
UPDATE users SET credits = credits - 10 WHERE user_id = 55;

-- Step 2: Record payment
INSERT INTO payments (user_id, amount) VALUES (55, 10.00);

-- If everything is okay:
COMMIT;

-- If step 2 fails (e.g., database error):
-- ROLLBACK; (Everything is undone, user gets their credits back)
```

## Transactions in FastAPI (SQLAlchemy)

In your FastAPI project, you don't usually write "BEGIN" manually. You use a Context Manager which handles the commit and rollback for you automatically.

```Python
from sqlalchemy.orm import Session

def process_purchase(db: Session, user_id: int, amount: float):
    try:
        # 'with' starts the transaction
        with db.begin():
            user = db.query(User).filter(User.id == user_id).first()
            user.balance -= amount
            # If an error happens here, SQLAlchemy triggers a ROLLBACK automatically
    except Exception:
        print("Transaction failed and was rolled back!")
```
