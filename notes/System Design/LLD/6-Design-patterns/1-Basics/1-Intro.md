# Design Patterns - Interview Revision Notes

## 1. Core Concepts
* **What is a Design Pattern?** A reusable, template-based solution to a recurring software design problem. It is a blueprint, not concrete code.
* **Origins:** Introduced by the **Gang of Four (GoF)** (Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides) in 1994.
* **Why Use Them?**
  * Establishes a shared design vocabulary among developers.
  * Promotes code reusability, modularity, and low coupling.
  * Prevents design anti-patterns.
* **Key Design Philosophies:**
  1. *Program to an interface, not an implementation* (Decouples client from concrete classes).
  2. *Favor object composition over class inheritance* (Has-a over Is-a; inheritance is static, composition is dynamic).

## 2. Design Principles vs. Design Patterns
* **Design Principles:** High-level guidelines/philosophy (e.g., **SOLID**, **DRY**, **KISS**). Abstract rules to follow.
* **Design Patterns:** Concrete structural blueprints (e.g., Factory, Strategy). Actionable designs/structures to implement.

## 3. Classifications & The 23 GoF Patterns
There are **23 classic GoF patterns**, categorized into 3 families:

### A. Creational Patterns (5)
*Focus: How objects are instantiated. Decouples creation logic from application logic.*
1. **Singleton:** Restricts instantiation to a single instance with a global access point. (e.g., Database connection pool).
2. **Factory Method:** Defines interface for creating objects, lets subclasses decide concrete type. (e.g., OS-specific UI button creation).
3. **Abstract Factory:** Creates families of related/dependent objects without specifying concrete classes. (e.g., Theme factory: light vs. dark scrollbar & button).
4. **Builder:** Constructs complex objects step-by-step. Separates representation and construction. (e.g., Custom HTTP Request builder, Document Parser).
5. **Prototype:** Clones existing objects using copy constructors/clone methods. Avoids subclassing creation. (e.g., Game entity spawning).

### B. Structural Patterns (7)
*Focus: How classes/objects compose to form larger structures while keeping them flexible.*
1. **Adapter:** Converts interface of a class to another expected by the client. (e.g., Wrapping 3rd party API format).
2. **Bridge:** Splits abstraction (interface) and implementation (logic) into separate hierarchies to grow independently. (e.g., Remote control vs. TV brands).
3. **Composite:** Composes objects into tree structures representing part-whole hierarchies. Clients treat individual and compositions uniformly. (e.g., Folder/File system, XML/JSON parsing).
4. **Decorator:** Dynamically adds behavior/responsibilities to an object without subclassing. (e.g., Encryption/Compression streams, UI scrollbar addition).
5. **Facade:** Provides a simplified, unified interface to a complex subsystem. (e.g., A client SDK that abstracts complex API calls).
6. **Flyweight:** Shares common state between similar objects to minimize memory footprint. (e.g., Game particles, character fonts).
7. **Proxy:** Placeholder/wrapper to control access, lazy load, or log operations. (e.g., Virtual/Caching/Protection proxy).

### C. Behavioral Patterns (11)
*Focus: How objects communicate, interact, and assign responsibilities.*
1. **Chain of Responsibility:** Passes requests along a chain of handlers; handler decides to process or delegate. (e.g., Web request middleware, Logging levels).
2. **Command:** Encapsulates a request/action as an object, allowing queuing, logging, or undo/redo. (e.g., Text editor undo/redo operations).
3. **Interpreter:** Evaluates language grammar/expressions. (e.g., Regex engine, SQL parser).
4. **Iterator:** Traverses elements of a collection sequentially without exposing underlying representation. (e.g., Custom tree/graph traversers).
5. **Mediator:** Centralizes communication between objects to prevent direct coupling. (e.g., Air traffic control tower, Chat room coordinator).
6. **Memento:** Captures and restores object internal state without violating encapsulation. (e.g., Undo history snapshots).
7. **Observer:** Pub-sub model. Objects subscribe to state changes of a subject to get notified automatically. (e.g., Event listeners, UI data binding).
8. **State:** Changes object behavior when its internal state changes (simulates changing class at runtime). (e.g., Vending machine transitions).
9. **Strategy:** Encapsulates a family of algorithms and makes them interchangeable at runtime. (e.g., Driving vs Walking routing, Sorting algorithms).
10. **Template Method:** Defines algorithm skeleton in a base class, deferring specific step implementations to subclasses. (e.g., Standard build pipeline).
11. **Visitor:** Separates algorithm operations from the object structure they operate on, adding features without changing class definitions. (e.g., XML/JSON exporter for tree nodes).

## 4. Quick Pitfalls & Criticisms (Interview FAQs)
* **Patternitis:** Forced usage of patterns leading to over-engineered, complex code.
* **Obsoletion:** In languages with first-class functions (Python, JS, Go), patterns like *Strategy*, *Command*, or *Iterator* are often native features or simple lambda functions.
