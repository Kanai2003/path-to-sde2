# Zomato LLD Case Study: Interview FAQ Cheat Sheet

This document compiles advanced questions and answers typically asked by interviewers evaluating candidate responses for SDE-2/SDE-3 roles on the Food Delivery LLD.

---

## FAQ & Discussion Points

### Q1: How do you make the Singleton pattern thread-safe in Python?
> **Answer**: Python's global interpreter lock (GIL) does not protect against race conditions when instantiating singletons. In a multi-threaded web application (like Uvicorn running FastAPI), multiple threads might check `cls not in cls._instances` simultaneously and instantiate duplicates.
> We solve this using a metaclass combined with a reentrant lock (`threading.Lock` or `threading.RLock`) during creation:
> ```python
> import threading
> 
> class SingletonMeta(type):
>     _instances = {}
>     _lock = threading.Lock()
> 
>     def __call__(cls, *args, **kwargs):
>         with cls._lock:
>             if cls not in cls._instances:
>                 cls._instances[cls] = super().__call__(*args, **kwargs)
>         return cls._instances[cls]
> ```

### Q2: What happens if a cart contains items from multiple restaurants? How does your design handle or prevent this?
> **Answer**: In our design, `Cart` contains a direct reference to a single `Restaurant`: `self.restaurant: Optional[Restaurant]`.
> When adding an item to the cart, the system checks:
> 1. If the cart is empty, set `self.restaurant` to the item's restaurant.
> 2. If the cart is not empty, check if the item's restaurant matches `self.restaurant`. If it doesn't match, raise an exception (e.g. `RestaurantMismatchException`).
> This prevents items from multiple restaurants in a single cart, which aligns with standard delivery workflows (since courier dispatching and logistics are optimized for a single pickup location).

### Q3: How would you scale the NotificationService asynchronously?
> **Answer**: The current `NotificationService` runs synchronously, which blocks the order flow while waiting for external SMTP/SMS APIs to respond.
> **To Scale**:
> 1. Decouple it using a Message Broker (like RabbitMQ, Kafka, or Redis Pub/Sub).
> 2. The `Tomato` orchestrator publishes an `OrderPlaced` event to a topic.
> 3. The `NotificationService` runs as a separate background worker consuming from that queue/topic.
> 4. In FastAPI, we can simulate this using `BackgroundTasks` to send the notification out-of-band:
> ```python
> from fastapi import BackgroundTasks
> 
> @app.post("/checkout")
> def checkout(request: CheckoutRequest, background_tasks: BackgroundTasks):
>     order = tomato.checkout(...)
>     background_tasks.add_task(notification_service.notify_user, order)
>     return order
> ```

### Q4: If the payment succeeds but saving the order to OrderManager fails, you have a consistency issue. How do you handle distributed transactions?
> **Answer**: This is a classic distributed systems problem (Saga pattern or 2-Phase Commit). At LLD level:
> 1. We must execute operations in a logical transactional unit.
> 2. If the database save operation fails, we must initiate a **compensating transaction** (refund the customer) through `payment_strategy.refund(transaction_id)`.
> 3. Alternatively, we can save the order in `PENDING_PAYMENT` state first, process payment, and then update to `PAID` or `FAILED`. This is idempotent and highly resilient.

### Q5: How would you extend this system to support discounts and promo codes?
> **Answer**: We can implement the **Decorator Pattern** or **Strategy Pattern** for promotions.
> Define an `IDiscountStrategy` with methods like `apply_discount(cart_total: float) -> float`.
> Concrete strategies include `PercentageDiscount`, `FlatDiscount`, and `BuyOneGetOneDiscount`.
> The `Cart.total_cost()` or the `Tomato` orchestrator can accept a discount strategy to apply before generating the final bill for checkout.
