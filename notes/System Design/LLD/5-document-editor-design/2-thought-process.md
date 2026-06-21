# LLD Case Study: Document Editor — Architectural Thought Process

This note outlines the architectural thought process behind transforming the fragile, monolithic document editor design into a decoupled, clean, and extensible system. This evolution mimics how you should explain your design decisions step-by-step during a live LLD interview.

---

## 1. Deconstructing the Monolith: Separation of Concerns

To evolve the design, we must separate the code along logical boundaries. In the bad design, `DocumentEditor` was a "God Object" doing everything. 

We can split the responsibilities into three distinct domains:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              DOCUMENT DOMAIN                              │
│  • What constitutes a document? (Document, TextElement, ImageElement)     │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
           ┌──────────────────────────┴──────────────────────────┐
           ▼                                                     ▼
┌──────────────────────────────────────┐     ┌──────────────────────────────┐
│          PERSISTENCE DOMAIN          │     │       RENDERING DOMAIN       │
│  • How do we save the document?      │     │  • How do we view/display?   │
│    (FileStorage, DBStorage)          │     │    (DocumentRenderer)        │
└──────────────────────────────────────┘     └──────────────────────────────┘
```

---

## 2. Applying Crucial Design Patterns

To decouple these domains, we apply specific design patterns that solve our SOLID violations.

### Pattern 1: Composite Pattern / Polymorphism (For Document Elements)
* **Problem**: The editor uses `vector<string>` with raw string parsing (`"TEXT:"`, `"IMAGE:"`) to differentiate types.
* **Solution**: Create an abstract base class `DocumentElement` with a contract method `render()`.
  * `TextElement` and `ImageElement` inherit from `DocumentElement` and implement their own version of `render()`.
  * The `Document` class now stores a collection of `DocumentElement` instances.
  * *Why this works (OCP)*: If we want to add a `TableElement`, we simply implement `DocumentElement`. The `Document` class and other components remain untouched. They simply call `element.render()` polymorphically.

### Pattern 2: Strategy Pattern (For Persistence)
* **Problem**: The editor is tightly coupled to saving to local files, which prevents database or cloud storage.
* **Solution**: Define an interface/abstract class `Persistence` with a `save(data: str)` method.
  * Concrete strategies like `FileStorage` and `DBStorage` implement this interface.
  * The `DocumentEditor` is injected with a `Persistence` object.
  * *Why this works (DIP & OCP)*: The editor depends on the `Persistence` abstraction. We can swap storage engines at runtime or add a `CloudStorage` class without modifying a single line of the editor code.

### Pattern 3: Separating the Presentation Layer (For Rendering)
* **Problem**: Rendering output is mixed directly into the data manipulation class.
* **Solution**: Extract rendering behavior into a dedicated `DocumentRenderer` class.
  * `DocumentRenderer` accepts a `Document` model and handles traversing and rendering each element.
  * This separates the **Model** (`Document` and its elements) from the **View** (`DocumentRenderer`).

---

## 3. Step-by-Step Refactoring Strategy

If asked by an interviewer how to refactor the monolithic class, follow this structured roadmap:

### Step 1: Encapsulate the Domain Models
Isolate data structures. Define what an "element" is. Instead of raw strings, represent elements as objects that contain both data and behavior.
* Create `DocumentElement` (Abstract).
* Create concrete subclasses (`TextElement`, `ImageElement`) containing attributes like `text` and `image_path`.
* Define `Document` as a container for these elements.

### Step 2: Extract low-level Persistence
Isolate I/O details.
* Define the `Persistence` interface.
* Move the text file saving code to a concrete `FileStorage` class.

### Step 3: Extract Presentation Logic
Move the console output logic out of the editor.
* Create a `DocumentRenderer` class. It accepts the `Document` object and calls the polymorphic `render()` method on each element.

### Step 4: Redefine the `DocumentEditor` (Controller)
Rebuild `DocumentEditor` as a thin controller/coordinator. It should:
* Hold a reference to a `Document` (the model).
* Hold a reference to a `Persistence` interface (the strategy).
* Expose clean APIs for operations (e.g., `add_text`, `save`).

---

## 4. Key Design Trade-offs & Decisions

During an SDE-2 interview, demonstrating awareness of trade-offs will set you apart:

| Design Dimension | Selected Approach | Trade-off / Alternatives Considered |
| :--- | :--- | :--- |
| **Element Rendering** | Elements implement `render()` internally. | **Alternative: Visitor Pattern**. If rendering logic varies widely (e.g., HTML rendering vs. PDF rendering vs. Console rendering), putting `render()` inside elements violates SRP. In that case, use the **Visitor Pattern** to separate element structures from their representation formats. For simpler systems, polymorphism is sufficient. |
| **Persistence Input** | `Persistence.save()` receives serialized data. | **Alternative**: Passing the entire `Document` object to `Persistence` allows the storage strategy to handle its own serialization (e.g., database fields vs. JSON text). We pass string/serialized data to keep storage strategies simple and decoupled from the domain model's structure. |
| **Object Creation** | Client instantiates elements directly. | **Alternative: Factory Pattern**. If element creation becomes complex (e.g., configuring fonts, margins, validation), a `DocumentElementFactory` should be introduced. |

---

## 5. Architectural Alignment Matrix (SOLID Refactoring)

> [!TIP]
> Use this quick-reference table to summarize how we mapped design flaws to SOLID principles:

| Monolithic Design Flaw | SOLID Principle Violated | Refactored Clean Design Solution |
| :--- | :--- | :--- |
| `DocumentEditor` handles document state, printing, and file saving. | **SRP** (Single Responsibility) | Split into `Document` (state), `DocumentRenderer` (view), and `Persistence` (I/O). |
| Adding a `Table` element requires modifying `render_document()` switch-cases. | **OCP** (Open-Closed) | Polymorphic `DocumentElement` base class. New elements inherit from it and define their own `render()`. |
| Editor is hardcoded to save files using local system commands. | **DIP** (Dependency Inversion) | Editor depends on the abstract `Persistence` interface. Concrete storage engines are injected. |

In the next note, [3-improved-design.md](file:///home/kanai/Dev/projects/path-to-sde2/notes/System%20Design/LLD/5-document-editor-design/3-improved-design.md), we implement this clean architecture in complete, ready-to-run Python code.
