# What is OOP?

OOP = Object-Oriented Programming. Way to structure code around **objects** (real-world things) instead of just functions and logic.

## Why OOP?

Without OOP — code becomes a mess of scattered functions, global variables, hard to maintain.

With OOP — code mirrors real world, easier to read, extend, reuse.

---

## Core Idea

Everything is an **object**. Object has:
- **Data** (what it knows) → fields/attributes
- **Behavior** (what it does) → methods/functions

```python
class Dog:
    name = "Bruno"        # data
    def bark(self):       # behavior
        print("Woof!")
```

---

## 4 Pillars

| Pillar | One line |
|---|---|
| **Abstraction** | Hide complexity, show only what's needed |
| **Encapsulation** | Bundle data + methods, protect internals |
| **Inheritance** | Child class reuses parent class code |
| **Polymorphism** | Same method, different behavior per class |

Each pillar has its own file. Start there after this.

---

## Class vs Object

- **Class** = blueprint (template)
- **Object** = actual instance (real thing made from blueprint)

```python
class Car:          # blueprint
    def drive(self): ...

my_car = Car()      # object (real instance)
```

**Analogy:** Class = cookie cutter. Object = the cookie.
