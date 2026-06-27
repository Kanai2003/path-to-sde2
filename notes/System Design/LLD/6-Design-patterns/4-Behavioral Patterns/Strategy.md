# Strategy Design Pattern - Interview Revision Notes

## 1. Quick Summary
* **Intent:** Defines a family of algorithms/behaviors, encapsulates each, and makes them interchangeable at runtime.
* **Core Philosophy:** **Favor composition over inheritance**. Decouples the client (context) from the concrete algorithms.
* **Analogy:** A robot with swappable modules (e.g., swapping a walking module for a flying module).

---

## 2. Why Use It? (The Problem vs. Solution)

### Bad Design (Inheritance)
* **Approach:** Having a base `Robot` class with methods `walk()`, `talk()`, `fly()`, and inheriting from it.
* **Issues:**
  1. **LSP Violation:** A `ToyRobot` inherits `fly()`, but cannot fly. Overriding it to throw `NotImplementedError` violates the Liskov Substitution Principle.
  2. **Code Duplication:** If two robot models share a custom `FastWalk` behavior but cannot inherit from the same parent, you must copy-paste the walk code.

### The Strategy Solution (Composition)
* Extract behaviors (`Walk`, `Talk`, `Fly`) into their own interface hierarchies.
* The `Robot` class (Context) holds references to these interfaces and delegates actions to them.

---

## 3. Python Code Implementation

```python
from abc import ABC, abstractmethod

# ==========================================
# 1. STRATEGY INTERFACES
# ==========================================
class TalkBehavior(ABC):
    @abstractmethod
    def talk(self) -> None:
        pass

class WalkBehavior(ABC):
    @abstractmethod
    def walk(self) -> None:
        pass

class FlyBehavior(ABC):
    @abstractmethod
    def fly(self) -> None:
        pass

# ==========================================
# 2. CONCRETE STRATEGIES
# ==========================================
class NormalTalk(TalkBehavior):
    def talk(self) -> None:
        print("Robot: 'Hello, how can I help you?'")

class NoTalk(TalkBehavior):
    def talk(self) -> None:
        print("Robot: (Blinks LED lights silently)")

class NormalWalk(WalkBehavior):
    def walk(self) -> None:
        print("Robot: Walking smoothly on two legs.")

class NoWalk(WalkBehavior):
    def walk(self) -> None:
        print("Robot: (Stationary)")

class NormalFly(FlyBehavior):
    def fly(self) -> None:
        print("Robot: Thrusters on! Flying.")

class NoFly(FlyBehavior):
    def fly(self) -> None:
        print("Robot: (Cannot fly)")

# ==========================================
# 3. CONTEXT (Client Wrapper)
# ==========================================
class Robot(ABC):
    def __init__(self, talk_strat: TalkBehavior, walk_strat: WalkBehavior, fly_strat: FlyBehavior):
        self._talk_strat = talk_strat
        self._walk_strat = walk_strat
        self._fly_strat = fly_strat

    # Delegation
    def perform_talk(self) -> None:
        self._talk_strat.talk()

    def perform_walk(self) -> None:
        self._walk_strat.walk()

    def perform_fly(self) -> None:
        self._fly_strat.fly()

    # Dynamic Strategy Setters (allows runtime updates)
    def set_talk_behavior(self, talk_strat: TalkBehavior) -> None:
        self._talk_strat = talk_strat

    def set_walk_behavior(self, walk_strat: WalkBehavior) -> None:
        self._walk_strat = walk_strat

    def set_fly_behavior(self, fly_strat: FlyBehavior) -> None:
        self._fly_strat = fly_strat

    @abstractmethod
    def projection(self) -> None:
        pass

# ==========================================
# 4. CONCRETE CONTEXT
# ==========================================
class CompanionRobot(Robot):
    def projection(self) -> None:
        print("CompanionR: Projecting holographic display.")

# ==========================================
# 5. DEMO
# ==========================================
if __name__ == "__main__":
    # Create companion robot (can talk, walk, but cannot fly)
    robot = CompanionRobot(NormalTalk(), NormalWalk(), NoFly())
    
    print("--- Initial State ---")
    robot.perform_talk()
    robot.perform_fly()

    print("\n--- Dynamically upgrading robot at runtime ---")
    robot.set_fly_behavior(NormalFly())
    robot.perform_fly()  # Swapped behavior on-the-fly!
```

---

## 4. Key Interview Takeaways

### Benefits (SOLID Alignment)
* **Open/Closed Principle (OCP):** Introduce new behaviors (e.g., `JetpackFly`) by creating a new class without modifying existing codebase.
* **Single Responsibility Principle (SRP):** Algorithm implementation is isolated from the main Context class.
* **Clean Code:** Replaces massive `if-else` or `switch` blocks (e.g., `if type == 'fast': walk_fast()`) with clean polymorphistic delegation (`self.walk_strat.walk()`).

### Strategy vs. State Pattern (Common Interview Question)
* **Strategy:** Behaviors are independent and configured from the *outside* (client injects the strategy). Strategies usually don't know about each other.
* **State:** Behaviors depend on internal state, and states *transition* between each other from the *inside* (e.g., `StateA` changes context to `StateB`).
