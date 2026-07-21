# LLD Case Study: Document Editor — The Initial "Bad" Design

This note analyzes the **initial monolithic design** of a Document Editor, identifying why it fails to meet production-grade software engineering standards. This analysis highlights design anti-patterns often discussed in SDE-2 system design interviews.

---

## 1. Structural Overview of the Bad Design

In the initial design, the entire document editor's capabilities are crammed into a single class: `DocumentEditor`.

```
┌──────────────────────────────────────────────────────────┐
│                      DocumentEditor                      │
├──────────────────────────────────────────────────────────┤
│ - elements: vector<string>                               │
├──────────────────────────────────────────────────────────┤
│ + addText(text: string): void                            │
│ + addImage(path: string): void                           │
│ + renderDocument(): void                                 │
│ + saveToFile(): void                                     │
└──────────────────────────────────────────────────────────┘
```

### Key Elements of This Design:
- **Data Storage**: A single list of strings (`vector<string> elements`) represents the entire document contents (both text and image paths are stored as strings).
- **Core Operations**: Adding text, adding images, rendering the document, and saving to a file are all handled by the same class.

---

## 2. Python Implementation of the Bad Design

Below is a Python implementation of the design shown in the UML diagram. This code demonstrates the internal coupling and fragile conditional logic typical of monolithic designs.

```python
import os
from typing import List

class DocumentEditor:
    def __init__(self):
        # Storing both text content and image file paths as raw strings in a single list
        self.elements: List[str] = []

    def add_text(self, text: str) -> None:
        # Prepend a marker to differentiate text from images
        self.elements.append(f"TEXT:{text}")
        print(f"Added text: '{text}'")

    def add_image(self, path: str) -> None:
        # Prepend a marker to differentiate images from text
        self.elements.append(f"IMAGE:{path}")
        print(f"Added image path: '{path}'")

    def render_document(self) -> None:
        """
        Renders the document to the console.
        Requires parsing string prefixes, which is extremely fragile.
        """
        print("\n--- Rendering Document ---")
        for element in self.elements:
            if element.startswith("TEXT:"):
                text_content = element[5:]
                print(f"[Text Element]: {text_content}")
            elif element.startswith("IMAGE:"):
                image_path = element[6:]
                # Bad: Tight coupling to rendering details (e.g., hardcoded console mock)
                print(f"[Image Element] Rendering image from path: {image_path}")
            else:
                # Fragile: Any new type of element will break this parsing logic
                raise ValueError("Unknown element type encountered!")
        print("--------------------------\n")

    def save_to_file(self, filepath: str) -> None:
        """
        Saves the document elements to a plain text file.
        """
        print(f"Saving document to {filepath}...")
        try:
            with open(filepath, 'w') as file:
                for element in self.elements:
                    file.write(element + "\n")
            print("Document saved successfully.")
        except IOError as e:
            print(f"Failed to save document: {e}")

# --- Client Usage Demonstration ---
if __name__ == "__main__":
    editor = DocumentEditor()
    editor.add_text("Hello, welcome to my document!")
    editor.add_image("/assets/images/diagram.png")
    editor.add_text("This is the concluding paragraph.")
    
    # Render document
    editor.render_document()
    
    # Save document
    editor.save_to_file("my_document.txt")
    
    # Cleanup
    if os.path.exists("my_document.txt"):
        os.remove("my_document.txt")
```

---

## 3. Detailed Analysis of Design Flaws (SOLID Violations)

In an SDE-2 interview, you must articulate *why* code is poorly designed using established architectural principles. Here is the breakdown:

### A. Violation of Single Responsibility Principle (SRP)
> **Definition**: A class should have one, and only one, reason to change.

`DocumentEditor` has **three distinct responsibilities**:
1. **Document State Management**: Maintaining the list of elements (`elements`).
2. **Rendering Logic**: Determining how elements are visualized on screen (`render_document`).
3. **Persistence Logic**: Directing how elements are saved and serialized (`save_to_file`).

*Consequence*: If the rendering output needs to change from plain text to HTML, or if we decide to save to a database instead of a file, we must modify the `DocumentEditor` class. This risks breaking unrelated functionality.

### B. Violation of Open-Closed Principle (OCP)
> **Definition**: Software entities should be open for extension, but closed for modification.

If we want to introduce a new type of document element—such as a **Table**, a **Hyperlink**, or a **CodeBlock**:
1. We must modify the `render_document` method to add a new `elif` branch to handle the new prefix.
2. We must modify `DocumentEditor` by adding a new method like `add_table(self, table_data)`.
3. We must update the serialization logic in `save_to_file`.

*Consequence*: The core editing class must be repeatedly modified for every new element type, violating OCP and introducing regression risks.

### C. Violation of Dependency Inversion Principle (DIP)
> **Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions.

`DocumentEditor` (high-level controller) directly depends on the low-level file write operations (`open(filepath, 'w')`).

*Consequence*: If the business requirements shift to save documents to Amazon S3, MongoDB, or Redis, we cannot do so without refactoring `DocumentEditor`. There is no abstraction layer (`Persistence` interface) to decouple the editor from the storage mechanism.

### D. Poor Data Modeling ("Primitive Obsession")
Storing structured elements inside a `List[str]` and using string prefixes (`"TEXT:"`, `"IMAGE:"`) to differentiate types is a severe anti-pattern known as **Primitive Obsession**.
- **No Type Safety**: A developer could append a string with the wrong prefix, causing a runtime exception.
- **Parsing Overhead**: The code must repeatedly slice and parse strings to recover the original data.
- **Scalability Limitation**: You cannot easily store metadata (e.g., font size for text, width/height for images) using plain strings without creating complex, unmaintainable string serialization formats.

---

## 4. Key Takeaways for SDE-2 Interviews

> [!WARNING]
> **Red Flags to Avoid in LLD Interviews**:
> 1. Writing classes that contain `if-else` or `switch` blocks checking string prefixes/types to determine behaviors. This indicates a missing polymorphic abstraction.
> 2. Hardcoding low-level details (like file I/O or DB drivers) directly inside business logic classes.
> 3. Mixing data models (the Document elements) with utilities (rendering, databases).

In the next note, [2-thought-process.md](file:///home/kanai/Dev/projects/path-to-sde2/notes/System%20Design/LLD/5-document-editor-design/2-thought-process.md), we will discuss the architectural thought process needed to systematically refactor this design into a highly scalable, SOLID-compliant system.
