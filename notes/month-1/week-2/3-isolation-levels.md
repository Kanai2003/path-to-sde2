# Isolation levels

# Isolation levels

In database terms, Isolation Levels are the settings that decide how much two people working in the same database at the same time can "see" each other's unfinished work.

Imagine a shared Google Doc where four people are writing. Isolation levels are the rules that prevent you from accidentally overwriting someone else's sentence or reading a paragraph they haven't finished typing yet.

## The 3 "Glitches" Isolation Prevents

Before looking at the levels, you must understand the three weird things that happen when people work simultaneously:

1. **Dirty Read**: You read a value that someone else changed, but then they hit "Undo" (Rollback). You now have "fake" data that never officially existed.

2. **Non-Repeatable Read**: You read a row, then someone else updates and saves it. You read it again 10 seconds later, and the value has changed in the middle of your task.

3. **Phantom Read**: You count all users (result: 10). Someone else adds a new user and saves. You count again, and now there are 11. A "phantom" user appeared out of nowhere.

## The 4 Levels of Isolation

Think of these like Security Clearances for your transactions. The higher the level, the more "locked down" and accurate the data is, but the slower the database becomes.

### 1. Read Uncommitted (The "Wild West")

The lowest level. You can see everything, even if it hasn't been saved yet.

- **Analogy**: Reading a draft over someone's shoulder while they are still typing.

- **Risk**: High. You will see "Dirty Reads" constantly.

### 2. Read Committed (The "Standard")

You can only see data that has been officially saved (committed).

- **Analogy**: You only see the Google Doc updates when the other person hits the "Save/Commit" button.

- **Note**: This is the default for PostgreSQL. It prevents Dirty Reads but still allows the other two glitches.

### 3. Repeatable Read (The "Snapshot")

Once you start your task, the database "freezes" the rows you looked at. Even if someone else saves changes, you won't see them until you finish your task.

- **Analogy**: You take a photocopy of the page you are working on. Even if the original book is edited, your photocopy stays the same.

- **Note**: This is the default for MySQL. It prevents Non-Repeatable reads.

### 4. Serializable (The "Single File Line")

The highest level. The database pretends you are the only person on earth. It runs transactions one after another in a perfect line.

- **Analogy**: Locking the entire library door so only you can enter. No one else can even walk in until you leave.

- **Risk**: Very slow. If many people try to use the database, they will all be stuck waiting in line.

## Summary

| Isolation Level  | Dirty Read   | Non-Repeatable Read | Phantom Read |
| ---------------- | ------------ | ------------------- | ------------ |
| Read Uncommitted | ❌ Allowed   | ❌ Allowed          | ❌ Allowed   |
| Read Committed   | ✅ Prevented | ❌ Allowed          | ❌ Allowed   |
| Repeatable Read  | ✅ Prevented | ✅ Prevented        | ❌ Allowed   |
| Serializable     | ✅ Prevented | ✅ Prevented        | ✅ Prevented |
