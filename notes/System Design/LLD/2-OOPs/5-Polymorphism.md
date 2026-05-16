# Polymorphism

> Same method name, different behavior depending on the object. "Many forms."

---

## Real World Example

`speak()` command sent to different animals:
- Dog → "Woof"
- Cat → "Meow"
- Duck → "Quack"

Same command. Different result. That's polymorphism.

---

## Two Types

### 1. Runtime Polymorphism (Method Overriding)

Child class **overrides** parent method. Behavior decided at runtime.

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class Duck(Animal):
    def speak(self):
        return "Quack!"

# Same code — different behavior per object
animals = [Dog(), Cat(), Duck()]
for animal in animals:
    print(animal.speak())  # Woof! / Meow! / Quack!
```

### 2. Compile-time Polymorphism (Method Overloading)

Same method name, different parameters. Python doesn't support natively — use default args.

```python
class Calculator:
    def add(self, a, b, c=0):   # handles 2 or 3 args
        return a + b + c

calc = Calculator()
calc.add(1, 2)      # 3
calc.add(1, 2, 3)   # 6
```

---

## Real App Example — Payment System

```python
class PaymentProcessor:
    def process(self, amount: float):
        raise NotImplementedError

class CreditCard(PaymentProcessor):
    def process(self, amount: float):
        print(f"Charged ₹{amount} to credit card")

class UPI(PaymentProcessor):
    def process(self, amount: float):
        print(f"Transferred ₹{amount} via UPI")

class Crypto(PaymentProcessor):
    def process(self, amount: float):
        print(f"Sent ₹{amount} in crypto")

def checkout(processor: PaymentProcessor, amount: float):
    processor.process(amount)   # doesn't care which one

checkout(CreditCard(), 1000)
checkout(UPI(), 500)
checkout(Crypto(), 250)
```

`checkout()` works with ANY payment type — past, present, future. Never changes. That's power of polymorphism.

---

## Key Points

- Enables **Open/Closed Principle** — open for extension, closed for modification
- New behavior = new class, not changing existing code
- Works hand-in-hand with Inheritance and Abstraction
- Makes code flexible and scalable
