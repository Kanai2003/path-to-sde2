# Zomato LLD Case Study: Design Patterns & Principles

This document explains the software engineering patterns and OOP principles implemented in our food delivery design, providing clear answers for LLD interviews.

---

## 1. Design Patterns Deep Dive

The architecture uses a blend of creational, structural, and behavioral patterns to decouple components and enforce separation of concerns.

### A. Factory Pattern (Creational)
- **Problem**: Creating an order depends on timing requirements. Immediate orders (`NowOrder`) have different initialization metadata compared to scheduled orders (`ScheduleOrder` with a future timestamp).
- **Solution**: We implement the **Factory Method Pattern**. 
  - `IOrderFactory` is the base interface.
  - `NowOrderFactory` and `ScheduleOrderFactory` act as concrete factories.
  - This allows the orchestrator to decouple the object creation logic from the execution logic. Adding new types of orders (e.g. `SubscriptionOrder`) only requires writing a new factory subclass, leaving the core checkout logic untouched.

```python
class IOrderFactory(ABC):
    @abstractmethod
    def create_order(self, user: User, restaurant: Restaurant, items: List[MenuItem], 
                     payment_strategy: IPaymentStrategy, fulfillment_mode: str, extra: str) -> Order:
        pass
```

### B. Strategy Pattern (Behavioral)
- **Problem**: The system supports multiple payment methods (UPI, Credit Card, NetBanking). Hardcoding conditionals (`if payment_method == 'UPI': ...`) violates the Open-Closed Principle and makes adding/removing payment services error-prone.
- **Solution**: We apply the **Strategy Pattern**.
  - `IPaymentStrategy` represents the abstract strategy.
  - `UPI`, `CreditCard`, and `NetBanking` are concrete strategies implementing a common `pay(amount)` interface.
  - The `Order` object is injected with the strategy polymorphically. When processing payments, it delegates to `self.strategy.pay(amount)`.

```python
class IPaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass
```

### C. Singleton Pattern (Creational)
- **Problem**: Shared data structures like the list of registered restaurants (`RestaurantManager`) or active orders (`OrderManager`) must remain centralized across the entire application context to avoid data inconsistency and save resources.
- **Solution**: We enforce the **Singleton Pattern** using Python's metaclasses. This prevents duplicate instantiation and ensures a single global point of access.

```python
class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()  # Ensures thread safety during instantiation

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
```

### D. Facade / Orchestrator Pattern (Structural)
- **Problem**: Placing an order involves multiple subsystems (finding user, validating restaurant, creating order via factory, executing payment strategy, logging in OrderManager, dispatching notification). If the client interacts with each subsystem directly, it creates heavy coupling.
- **Solution**: The `Tomato` class acts as the **Orchestrator** (similar to a Facade/Controller). It exposes a unified `checkout` interface to the client, coordinating interactions behind the scenes.

---

## 2. SOLID Principles Applied

| Principle | How It is Satisfied in the Design |
| :--- | :--- |
| **S**ingle Responsibility (SRP) | Each class has one focus. `Cart` only manages items and prices. `NotificationService` only alerts users. `OrderManager` only tracks orders. |
| **O**pen-Closed (OCP) | We can add a new payment strategy (e.g. `CryptoPayment`) or a new order factory (e.g. `GroupOrderFactory`) by extending the base class without modifying existing components. |
| **L**iskov Substitution (LSP) | Subclasses like `DeliveryOrder` and `PickupOrder` can be used interchangeably wherever the base `Order` class is expected without breaking the application logic. |
| **I**nterface Segregation (ISP) | Rather than creating a giant monolithic manager or strategy, we separate `IPaymentStrategy`, `IOrderFactory`, and `NotificationService` so classes only depend on methods they actually need. |
| **D**ependency Inversion (DIP) | The `Order` class relies on the abstraction `IPaymentStrategy` instead of concrete classes like `CreditCard` or `UPI`. The strategy is dynamically injected at runtime. |
