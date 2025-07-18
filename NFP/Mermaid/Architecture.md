---mermaid
graph TD
A[User Interface] --> B[Website Wizard]
B --> C[Step 1: Restaurant Basics]
B --> D[Step 2: Page Selection]
B --> E[Step 3: Design Preferences]
B --> F[Step 4: Review & Generate]

    C --> G[Form Data Collection]
    D --> G
    E --> G

    G --> H[Website Generation]

    H --> I[Hugo Static Site]
    H --> J[Custom Theme]
    H --> K[Content Generation]

    I --> L[Final Website]
    J --> L
    K --> L

    L --> M[Preview System]
    L --> N[Download Package]

    subgraph Features
        O[Form Validation]
        P[Real-time Preview]
        Q[Operating Hours]
        R[Logo Management]
        S[Color Schemes]
    end
---
