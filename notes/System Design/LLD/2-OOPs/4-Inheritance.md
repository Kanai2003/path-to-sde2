# Inheritance

> Child class gets all properties and methods of parent class. Reuse code, extend behavior.

---

## Real World Example

All vehicles have: `start()`, `stop()`, `fuel_type`

Car, Bike, Truck don't each rewrite those — they **inherit** from `Vehicle` and only add what's unique.

---

## Code Example

```python
class Vehicle:
    def __init__(self, brand: str, fuel: str):
        self.brand = brand
        self.fuel = fuel

    def start(self):
        print(f"{self.brand} started")

    def stop(self):
        print(f"{self.brand} stopped")


class Car(Vehicle):  # inherits Vehicle
    def __init__(self, brand: str):
        super().__init__(brand, fuel="Petrol")

    def open_trunk(self):          # Car-specific behavior
        print("Trunk opened")


class ElectricCar(Car):            # inherits Car → inherits Vehicle
    def __init__(self, brand: str):
        super().__init__(brand)
        self.fuel = "Electric"

    def charge(self):              # ElectricCar-specific
        print("Charging...")


tesla = ElectricCar("Tesla")
tesla.start()        # from Vehicle
tesla.open_trunk()   # from Car
tesla.charge()       # own method
```

---

## 5 Types of Inheritance

### 1. Single Inheritance

One child, one parent. Most common.

```
Vehicle
  └── Car
```

```python
class Vehicle:
    def start(self): print("Starting")

class Car(Vehicle):      # Car IS-A Vehicle
    def honk(self): print("Beep!")
```

---

### 2. Multi-level Inheritance

Chain: grandparent → parent → child.

```
Vehicle
  └── Car
        └── ElectricCar
```

```python
class Vehicle:
    def start(self): print("Starting")

class Car(Vehicle):
    def open_trunk(self): print("Trunk open")

class ElectricCar(Car):           # gets BOTH Vehicle + Car
    def charge(self): print("Charging")

tesla = ElectricCar()
tesla.start()       # from Vehicle
tesla.open_trunk()  # from Car
tesla.charge()      # own
```

---

### 3. Multiple Inheritance

One child, multiple parents. Python supports. Java does NOT (use interfaces instead).

```
  Flyable    Car
      └──────┘
       FlyingCar
```

```python
class Car:
    def drive(self): print("Driving")

class Airplane:
    def fly(self): print("Flying")

class FlyingCar(Car, Airplane):   # inherits both
    pass

fc = FlyingCar()
fc.drive()   # from Car
fc.fly()     # from Airplane
```

> **Interview tip:** Java avoids multiple inheritance to prevent **Diamond Problem** (ambiguity when two parents have same method). Java uses `interface` instead.

---

### 4. Hierarchical Inheritance

One parent, multiple children. Each child gets same parent but adds its own behavior.

```
      Vehicle
    ┌────┼────┐
   Car  Bike  Truck
```

```python
class Vehicle:
    def start(self): print("Starting")

class Car(Vehicle):
    def open_trunk(self): print("Trunk open")

class Bike(Vehicle):
    def do_wheelie(self): print("Wheelie!")

class Truck(Vehicle):
    def load_cargo(self): print("Loading cargo")

# All share start() from Vehicle, each has unique method
```

---

### 5. Hybrid Inheritance

Mix of two or more types above. Common in real systems.

```
        Vehicle
          |
     ┌─────────┐
  Airplane    Car
     └────────┘
      FlyingCar        ← Multi-level + Multiple combined
```

```python
class Vehicle:
    def start(self): print("Starting")

class Car(Vehicle):              # Single
    def drive(self): print("Driving")

class Airplane(Vehicle):         # Single
    def fly(self): print("Flying")

class FlyingCar(Car, Airplane):  # Multiple → makes it Hybrid
    pass

fc = FlyingCar()
fc.start()   # from Vehicle (via Car)
fc.drive()   # from Car
fc.fly()     # from Airplane
```

> **MRO (Method Resolution Order):** Python uses C3 algorithm to resolve which parent's method gets called. Check with `FlyingCar.__mro__`.

---

## Quick Cheat Sheet

| Type             | Structure           | Key Note                              |
| ---------------- | ------------------- | ------------------------------------- |
| **Single**       | A → B               | Simplest, cleanest                    |
| **Multi-level**  | A → B → C           | Chain, watch depth                    |
| **Multiple**     | A+B → C             | Python yes, Java no (Diamond Problem) |
| **Hierarchical** | A → B, A → C, A → D | One parent many children              |
| **Hybrid**       | Mix of above        | Complex, use carefully                |

---

## Key Points

- `super()` calls parent constructor/method
- Child **overrides** parent method to change behavior (→ Polymorphism)
- Promotes **DRY** (Don't Repeat Yourself)
- Don't abuse — deep inheritance chains are hard to debug

## When NOT to use

Prefer **composition over inheritance** when:

- Child is not truly a "type of" parent
- Relationship is "has-a" not "is-a"

```python
# Bad: Engine is not a Car
class Car(Engine): ...

# Good: Car HAS an Engine
class Car:
    def __init__(self):
        self.engine = Engine()
```
