# SOLID — Quick Interview Cheat-sheet

- **S — Single Responsibility Principle**: A class should have one, and only one, reason to change. Keep responsibilities focused. Example: separate persistence, validation, and notification into different classes.

- **O — Open/Closed Principle**: Open for extension, closed for modification. Use abstractions (interfaces/abstract classes) so new behavior is added by new classes rather than editing old ones.

- **L — Liskov Substitution Principle**: Subtypes must be substitutable for their base types without changing correctness. If a subtype breaks the base contract, extract a narrower interface.

- **I — Interface Segregation Principle**: Clients should not be forced to depend on interfaces they do not use. Split large interfaces into role-specific ones (`Workable`, `Feedable`).

- **D — Dependency Inversion Principle**: Depend on abstractions, not concretions. Inject dependencies (constructor injection) and keep a single composition root.

## Quick Examples (one-liners)

- SRP: `UserRepository.save(user)` vs `User.send_welcome_email()` — separate responsibilities.
- OCP: `ReportGenerator` accepts `Report` interface; add new `JSONReport` class to extend.
- LSP: `WithdrawableAccount` vs `FixedDepositAccount` — don't force unsupported operations.
- ISP: `Workable` and `Feedable` instead of a single `Worker` interface.
- DIP: `CheckoutService(payment_processor: PaymentProcessor)` — inject `StripeProcessor` or `PayPalProcessor`.

## Interview talking points (30s answers)

- SOLID reduces coupling, improves testability, and makes code easier to change safely.
- There are trade-offs: more files, more abstractions; avoid premature over-engineering.
- Use pragmatic judgment: refactor toward SOLID as code evolves and smells appear (large classes, many conditionals, NotImplementedError in subclasses).

## Design-review checklist

- Are classes small and cohesive (SRP)?
- Can new features be added without editing existing classes (OCP)?
- Are subclasses truly substitutable (LSP)?
- Do clients depend only on the methods they use (ISP)?
- Do high-level modules depend on abstractions (DIP)?

--
_File: `/notes/System Design/LLD/3-SOLID-design-principles/SOLID-summary.md`_
