# LLD Case Study: Document Editor — The Clean, SOLID-Compliant Design

This note presents the **improved, SOLID-compliant design** of the Document Editor, providing the complete Python implementation and showing how the architecture easily accommodates future extensions.

---

## 1. Clean Design Class Architecture

Based on the improved UML diagram, the system is decomposed into decoupled, highly cohesive classes:

```
                          ┌─────────────────────┐
                          │  DocumentElement    │◄─────────────────┐
                          ├─────────────────────┤                  │ (1..*)
                          │ + render(): void    │                  │
                          └──────────▲──────────┘                  │
                                     │                             │
                     ┌───────────────┴───────────────┐             │
                     │                               │             │
          ┌──────────────────┐            ┌──────────────────┐     │
          │   TextElement    │            │   ImageElement   │     │
          ├──────────────────┤            ├──────────────────┤     │
          │ + render(): void │            │ + render(): void │     │
          └──────────────────┘            └──────────────────┘     │
                                                                   │
 ┌─────────────────────────────────────────────────────────────────┼───┐
 │   DocumentRenderer   │                                          │   │
 ├──────────────────────┤         ┌──────────────────┐             │   │
 │ - doc: Document      │         │     Document     │─────────────┘   │
 ├──────────────────────┤         ├──────────────────┤                 │
 │ + render(): void     │         │ - elements: List │                 │
 └──────────────────────┘         ├──────────────────┤                 │
                                  │ + addElement()   │                 │
                                  │ + getElements()  │◄────────────┐   │
                                  └──────────────────┘             │   │
                                                                   │   │
                                  ┌──────────────────┐             │   │
                                  │   Persistence    │             │   │
                                  ├──────────────────┤             │   │
                                  │ + save(data): void             │   │
                                  └──────────▲───────┘             │   │
                                             │                     │   │
                             ┌───────────────┴───────────────┐     │   │
                             │                               │     │   │
                  ┌──────────────────┐            ┌──────────┴───────┐ │
                  │   FileStorage    │            │    DBStorage     │ │
                  ├──────────────────┤            ├──────────────────┤ │
                  │ + save(data): void            │ + save(data): void │
                  └──────────────────┘            └──────────────────┘ │
                                                                       │
                                  ┌──────────────────┐                 │
                                  │  DocumentEditor  │─────────────────┘
                                  ├──────────────────┤
                                  │ - doc: Document  │
                                  │ - storage: Persis│
                                  ├──────────────────┤
                                  │ + addText()      │
                                  │ + addImage()     │
                                  └──────────────────┘
```

---

## 2. Complete Python Implementation

Here is the production-grade, object-oriented Python implementation using `abc` for interfaces and `typing` for clear contracts.

```python
from abc import ABC, abstractmethod
from typing import List

# ==========================================
# 1. DOMAIN LAYER: DOCUMENT ELEMENTS (Composite)
# ==========================================

class DocumentElement(ABC):
    """
    Abstract interface for all components that can exist inside a Document.
    Acts as the base Component in the Composite Design Pattern.
    """
    @abstractmethod
    def render(self) -> str:
        """Returns a string representation of the rendered element."""
        pass

class TextElement(DocumentElement):
    """Concrete implementation of a Text element."""
    def __init__(self, text: str):
        self.text = text

    def render(self) -> str:
        return f"[Text Element]: {self.text}"

class ImageElement(DocumentElement):
    """Concrete implementation of an Image element."""
    def __init__(self, path: str):
        self.path = path

    def render(self) -> str:
        return f"[Image Element] Rendering image from: {self.path}"


# ==========================================
# 2. DOMAIN LAYER: DOCUMENT CONTAINER
# ==========================================

class Document:
    """
    Model class that represents the document structure.
    Has the single responsibility of managing the list of DocumentElements.
    """
    def __init__(self):
        self._elements: List[DocumentElement] = []

    def add_element(self, element: DocumentElement) -> None:
        self._elements.append(element)

    def get_elements(self) -> List[DocumentElement]:
        return self._elements


# ==========================================
# 3. PRESENTATION LAYER: RENDERING
# ==========================================

class DocumentRenderer:
    """
    Handles presentation logic. Decoupled from the Document model
    so rendering formats (HTML, PDF, Markdown) can evolve separately.
    """
    def __init__(self, doc: Document):
        self._doc = doc

    def render(self) -> None:
        print("\n--- Document Rendering Start ---")
        for element in self._doc.get_elements():
            # Polymorphic call: Each element knows how to render itself
            print(element.render())
        print("--- Document Rendering End ---\n")


# ==========================================
# 4. PERSISTENCE LAYER (Strategy Pattern)
# ==========================================

class Persistence(ABC):
    """Abstract interface defining the Persistence strategy."""
    @abstractmethod
    def save(self, data: str) -> None:
        pass

class FileStorage(Persistence):
    """Concrete Persistence strategy that saves to the file system."""
    def __init__(self, filepath: str):
        self.filepath = filepath

    def save(self, data: str) -> None:
        print(f"[FileStorage] Writing data to disk at '{self.filepath}'...")
        with open(self.filepath, 'w') as file:
            file.write(data)
        print("[FileStorage] Write successful.")

class DBStorage(Persistence):
    """Concrete Persistence strategy that saves to a Database."""
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def save(self, data: str) -> None:
        print(f"[DBStorage] Connecting to database at '{self.connection_string}'...")
        print(f"[DBStorage] Inserting serialized document: {data[:60]}...")
        print("[DBStorage] Transaction committed.")


# ==========================================
# 5. CONTROLLER LAYER: DOCUMENT EDITOR
# ==========================================

class DocumentEditor:
    """
    Coordinator class (Controller) that acts as the entry point for editing.
    It links the Document model with the chosen Persistence strategy.
    """
    def __init__(self, doc: Document, storage: Persistence):
        self._doc = doc
        self._storage = storage  # Dependent on abstraction, not implementation (DIP)

    def add_text(self, text: str) -> None:
        element = TextElement(text)
        self._doc.add_element(element)

    def add_image(self, path: str) -> None:
        element = ImageElement(path)
        self._doc.add_element(element)

    def save_document(self) -> None:
        """Serializes the document elements and saves them via the storage strategy."""
        # Serialize the document elements (simple format for demonstration)
        serialized_data = "\n".join([el.render() for el in self._doc.get_elements()])
        self._storage.save(serialized_data)


# ==========================================
# 6. CLIENT CODE (Usage Demo)
# ==========================================
if __name__ == "__main__":
    import os

    # 1. Initialize core document model
    my_doc = Document()
    
    # 2. Select a storage strategy (e.g., FileStorage)
    filepath = "clean_document.txt"
    file_strategy = FileStorage(filepath)
    
    # 3. Inject dependencies into the Editor
    editor = DocumentEditor(my_doc, file_strategy)
    
    # 4. Perform edits
    editor.add_text("Welcome to the SOLID Document Editor!")
    editor.add_image("/images/architecture.png")
    editor.add_text("This design easily satisfies SDE-2 requirements.")
    
    # 5. Render document (via DocumentRenderer)
    renderer = DocumentRenderer(my_doc)
    renderer.render()
    
    # 6. Save document using the configured strategy
    editor.save_document()

    # 7. Demonstrate database swap (Runtime configuration)
    print("\n--- Swapping Storage Engine at Runtime ---")
    db_strategy = DBStorage("postgresql://admin:secret@localhost:5432/docs")
    editor._storage = db_strategy  # Can be dynamically swapped
    editor.save_document()
    
    # Clean up file artifact
    if os.path.exists(filepath):
        os.remove(filepath)
```

---

## 3. Extending the Design Without Modifying Existing Code (OCP Proof)

To prove to your interviewer that this design complies with the Open-Closed Principle, let's look at how we extend it:

### Adding a new Document Element type:
Suppose we need to add a `TableElement`. We do **not** touch `DocumentEditor`, `Document`, or `DocumentRenderer`. We simply write:
```python
class TableElement(DocumentElement):
    def __init__(self, rows: List[List[str]]):
        self.rows = rows

    def render(self) -> str:
        # Custom table rendering logic
        rendered_rows = [" | ".join(row) for row in self.rows]
        border = "-" * len(rendered_rows[0])
        return f"[Table Element]\n{border}\n" + "\n".join(rendered_rows) + f"\n{border}"
```

### Adding a new Persistence Engine:
Suppose we want to save documents to Cloud storage (e.g., Amazon S3). We write:
```python
class S3Storage(Persistence):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name

    def save(self, data: str) -> None:
        print(f"[S3Storage] Uploading document to bucket: '{self.bucket_name}'...")
```

---

## 4. SDE-2 Interview Cheat Sheet & FAQ

### Q1: How does this design address the Dependency Inversion Principle (DIP)?
> **Answer**: `DocumentEditor` does not instantiate or directly depend on `FileStorage` or `DBStorage`. Instead, it depends on the `Persistence` abstraction. The specific storage engine is passed to it during instantiation (Dependency Injection). This isolates the editor from I/O detail changes.

### Q2: What design patterns are used here, and why?
> **Answer**: 
> 1. **Composite / Polymorphism**: `DocumentElement` is the component interface, implemented by concrete elements. This allows the document to handle all element types uniformly.
> 2. **Strategy Pattern**: The `Persistence` interface serves as the abstraction for saving strategies (`FileStorage`, `DBStorage`), enabling run-time algorithm swapping.
> 3. **MVC-like Separation**: The `Document` behaves as the Model, `DocumentRenderer` as the View, and `DocumentEditor` as the Controller.

### Q3: How would you handle complex document serialization (e.g. converting to HTML vs PDF)?
> **Answer**: Right now, elements contain their own simple `render()` method, which is sufficient for simple use cases. However, if we need to export the document to drastically different formats (like Markdown, HTML, and PDF), having elements manage all these format conversions violates SRP.
> 
> To resolve this, I would use the **Visitor Pattern**. I would define a `DocumentVisitor` interface with methods like `visit_text(TextElement)` and `visit_image(ImageElement)`. I would then create concrete visitors like `HTMLExportVisitor` and `PDFExportVisitor`. This separates the document structures from their format-specific representation logic.
