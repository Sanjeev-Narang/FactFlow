# FactFlow 

The production App for the PDF Fact-Check Analysis platform. Built with Django, Python 3.13, and PostgreSQL, optimized with a stateless architectural design.

## Key Architecture Features
* **Stateless PDF Processing**: Zero physical storage writes for uploaded documents to guarantee enterprise-level data privacy.
* **Concurrent Fact-Checking**: Leverages multi-threading with optimized minimal thread pools to process extracted claims in parallel.
* **Automated Live Search**: Integrates with concurrent search endpoints to cross-reference statements across web indices dynamically.

---

## The Lifecycle of Your PDF File

The backend pipeline processes files fluidly using a strict **RAM-only lifecycle**:

```mermaid
graph TD 
    A[User Upload] --> B[1. Request In RAM] 
    B --> C[2. Database Entry] 
    C --> D[3. RAM Parsing] 
    D --> E[4. Garbage Cleanup]

    style A fill:#2d3748,stroke:#4a5568,stroke-width:2px,color:#fff
    style B fill:#1a202c,stroke:#4a5568,stroke-width:1px,color:#fff
    style C fill:#1a202c,stroke:#4a5568,stroke-width:1px,color:#fff
    style D fill:#1a202c,stroke:#4a5568,stroke-width:1px,color:#fff
    style E fill:#1a202c,stroke:#4a5568,stroke-width:1px,color:#fff
```

