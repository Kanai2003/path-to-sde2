# Abstraction

> Hide complexity. Show only what's necessary.

User doesn't need to know HOW it works — just WHAT it does.

---

## Real World Example

You drive a car. You press accelerator — car moves.
You don't know: fuel injection, engine combustion, gear mechanics.

That complexity is **hidden**. You only see: `accelerate()`, `brake()`, `steer()`.

---

## Code Example

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass  # HOW to pay is hidden from caller

class StripePayment(PaymentProcessor):
    def pay(self, amount: float) -> bool:
        # Stripe-specific logic hidden here
        print(f"Paid ₹{amount} via Stripe")
        return True

class UPIPayment(PaymentProcessor):
    def pay(self, amount: float) -> bool:
        # UPI-specific logic hidden here
        print(f"Paid ₹{amount} via UPI")
        return True

# Caller only knows: call .pay() — doesn't care how
processor = StripePayment()
processor.pay(500)
```

Caller just calls `pay()`. No idea what happens inside. That's abstraction.

---

## Key Points

- Achieved via **abstract classes** and **interfaces**
- Reduces complexity for the user of the class
- Forces subclasses to implement the contract
- Different from Encapsulation (see `3-Encapsulation.md`)

## Abstraction vs Encapsulation (common confusion)

| | Abstraction | Encapsulation |
|---|---|---|
| Focus | Hide complexity (design level) | Hide data (implementation level) |
| How | Abstract class / Interface | Private fields + getters/setters |
| Goal | What object does | How object protects its data |
