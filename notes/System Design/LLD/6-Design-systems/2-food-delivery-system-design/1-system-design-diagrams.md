# Zomato LLD Case Study: Food Delivery System Diagrams

This document outlines the **Low-Level Design (LLD)** requirements, the **Class Diagram** (based on the system whiteboard design), and a **Sequence Diagram** showing the interaction flow during order placement.

---

## 1. System Requirements & Scope

1. **User Management**: Users have profiles with an ID, name, address, and a dynamic shopping Cart.
2. **Restaurant & Catalog Management**: Restaurants have locations and menus composed of multiple MenuItems (each with a code, name, and price).
3. **Cart Operations**: Users can add items from a single restaurant to their cart, retrieve the total cost, and check if the cart is empty.
4. **Order Factory (Factory Pattern)**: Orders can be placed either for immediate delivery (`NowOrder`) or scheduled for a later time (`ScheduleOrder`). The corresponding factories (`NowOrderFactory`, `ScheduleOrderFactory`) instantiate the appropriate objects.
5. **Order Types**: The system supports two primary fulfillment modes:
   - `DeliveryOrder`: Handled by a rider, delivered to the user's address.
   - `PickupOrder`: Prepared by the restaurant, picked up by the user directly.
6. **Payment System (Strategy Pattern)**: Customers can choose different payment methods: `CreditCard`, `NetBanking`, or `UPI`. The system invokes the chosen strategy polymorphically.
7. **Order Coordination & Management**:
   - `OrderManager` (Singleton) tracks active and past orders.
   - `RestaurantManager` (Singleton) manages restaurant registries and search queries.
   - `Tomato` (Orchestrator Class) acts as the facade/mediator that ties everything together.
8. **Notifications**: When an order is placed successfully, the `NotificationService` notifies the customer.

---

## 2. Low-Level Design Class Diagram

Below is the **Mermaid Class Diagram** representing the exact UML structure depicted on the system whiteboard design:

```mermaid
classDiagram
    class Tomato {
        +checkout(userId: int, paymentMethod: string, orderType: string, fulfillmentMode: string, scheduleTime: string) Order
    }
    
    class Cart {
        -restaurant: Restaurant
        -items: List~MenuItem~
        +addToCart(item: MenuItem) void
        +totalCost() float
        +isEmpty() bool
        +clear() void
    }
    
    class User {
        +userId: int
        +name: String
        +address: String
        +cart: Cart
    }
    
    class RestaurantManager {
        <<Singleton>>
        -restaurants: List~Restaurant~
        +addRestaurant(restaurant: Restaurant) void
        +searchByLoc(loc: String) List~Restaurant~
        +getRestaurantById(id: int) Restaurant
    }
    
    class Restaurant {
        <<Model>>
        +restaurantId: int
        +name: String
        +loc: String
        +menu: List~MenuItem~
    }
    
    class MenuItem {
        <<Model>>
        +code: String
        +name: String
        +price: float
    }
    
    class IPaymentStrategy {
        <<Interface>>
        +pay(amount: float) bool
    }
    
    class CreditCard {
        +pay(amount: float) bool
    }
    
    class NetBanking {
        +pay(amount: float) bool
    }
    
    class UPI {
        +pay(amount: float) bool
    }

    IPaymentStrategy <|-- CreditCard
    IPaymentStrategy <|-- NetBanking
    IPaymentStrategy <|-- UPI
    
    class IOrderFactory {
        <<Interface>>
        +createOrder(user: User, restaurant: Restaurant, items: List~MenuItem~, strategy: IPaymentStrategy, fulfillmentMode: string, addressOrRes: string) Order
    }
    
    class ScheduleOrderFactory {
        +scheduleTime: String
        +createOrder(user: User, restaurant: Restaurant, items: List~MenuItem~, strategy: IPaymentStrategy, fulfillmentMode: string, addressOrRes: string) Order
    }
    
    class NowOrderFactory {
        +createOrder(user: User, restaurant: Restaurant, items: List~MenuItem~, strategy: IPaymentStrategy, fulfillmentMode: string, addressOrRes: string) Order
    }
    
    IOrderFactory <|-- ScheduleOrderFactory
    IOrderFactory <|-- NowOrderFactory
    
    class Order {
        <<Abstract>>
        +id: int
        +user: User
        +restaurant: Restaurant
        +items: List~MenuItem~
        +strategy: IPaymentStrategy
        +getType() String
        +processPayment() bool
    }
    
    class DeliveryOrder {
        +address: String
        +getType() String
    }
    
    class PickupOrder {
        +resAddress: String
        +getType() String
    }
    
    Order <|-- DeliveryOrder
    Order <|-- PickupOrder
    
    class OrderManager {
        <<Singleton>>
        -ordersList: List~Order~
        +addOrder(order: Order) void
        +listOrders() List~Order~
    }
    
    class NotificationService {
        +notifyUser(order: Order) void
    }

    %% Relationships
    User "1" --> "1" Cart : has
    Cart "*" --> "1" Restaurant : references
    Cart "*" --> "*" MenuItem : contains
    RestaurantManager "1" --> "*" Restaurant : aggregates
    Restaurant "1" --> "*" MenuItem : contains
    Tomato ..> User : queries
    Tomato ..> RestaurantManager : queries
    Tomato ..> IOrderFactory : uses
    Tomato ..> OrderManager : registers orders
    Tomato ..> NotificationService : sends alerts
    Order "1" --> "1" User : placed_by
    Order "1" --> "1" Restaurant : details_from
    Order "*" --> "*" MenuItem : items_list
    Order "1" --> "1" IPaymentStrategy : uses
    OrderManager "1" --> "*" Order : manages
```

---

## 3. Order Flow Sequence Diagram

Here is how the orchestration class `Tomato` coordinates the order placement process among the subsystems:

```mermaid
sequenceDiagram
    autonumber
    actor Customer as User
    participant App as Tomato (Orchestrator)
    participant RM as RestaurantManager
    participant Factory as IOrderFactory
    participant Ord as Order (Delivery/Pickup)
    participant Pay as IPaymentStrategy
    participant OM as OrderManager
    participant Notif as NotificationService

    Customer->>App: checkout(userId, paymentMethod, orderType, fulfillmentMode, extraDetails)
    App->>RM: getRestaurantById(cart.restaurant.id)
    RM-->>App: Restaurant info
    Note over App: Instantiates appropriate IPaymentStrategy<br/>(CreditCard, NetBanking, UPI)
    Note over App: Instantiates appropriate IOrderFactory<br/>(NowOrderFactory, ScheduleOrderFactory)
    App->>Factory: createOrder(user, restaurant, cart.items, strategy, fulfillmentMode, address)
    Factory->>Ord: Instantiate DeliveryOrder/PickupOrder
    Ord-->>Factory: Order Instance
    Factory-->>App: Order Instance
    App->>Ord: processPayment()
    Ord->>Pay: pay(totalCost)
    Pay-->>Ord: paymentSuccess (True)
    Ord-->>App: paymentSuccess (True)
    
    alt Payment Succeeded
        App->>OM: addOrder(order)
        OM-->>App: Order Saved
        App->>Notif: notifyUser(order)
        Notif-->>Customer: Order Confirmation Notification
        App->>Customer: Order Success Response (Order Details & ID)
    else Payment Failed
        App->>Customer: Order Failed Response (Payment Failed)
    end
```
