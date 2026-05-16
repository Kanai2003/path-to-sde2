# Encapsulation

> Bundle data + methods together. Protect internal state from outside interference.

Don't let outsiders directly touch your data. Force them to go through controlled methods.

---

## Real World Example

ATM machine:
- You can't directly access the cash inside
- You go through: `insert_card()` → `enter_pin()` → `withdraw()`
- Internal logic (balance check, ledger update) is **protected**

---

## Code Example — Without Encapsulation (Bad)

```python
class BankAccount:
    balance = 1000  # public — anyone can change!

account = BankAccount()
account.balance = -99999  # 💀 no validation, no protection
```

## Code Example — With Encapsulation (Good)

```python
class BankAccount:
    def __init__(self, balance: float):
        self.__balance = balance  # private (__ prefix)

    def deposit(self, amount: float):
        if amount > 0:
            self.__balance += amount

    def withdraw(self, amount: float):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
        else:
            raise ValueError("Insufficient funds")

    def get_balance(self) -> float:
        return self.__balance  # controlled read-only access

account = BankAccount(1000)
account.withdraw(200)
print(account.get_balance())  # 800
# account.__balance = -99999  # ❌ AttributeError — protected!
```

---

## Key Points

- Use `private` fields (`__` in Python, `private` in Java)
- Expose only what's needed via public methods
- Validation logic lives inside the class — one place
- Prevents invalid state from outside

## Benefits

| | Without | With |
|---|---|---|
| Data safety | Anyone modifies anything | Controlled via methods |
| Validation | Scattered everywhere | Inside the class |
| Change impact | Break entire codebase | Change internals freely |
