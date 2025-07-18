---mermaid
graph TD
A[Start] --> B[Initialize WebsiteWizard]
B --> C[Step 1: Restaurant Basics]
C --> D[Step 2: Website Pages]
D --> E[Step 3: Design Preferences]
E --> F[Step 4: Review & Generate]

    C -->|Input| C1[Restaurant Info]
    C1 -->|Validate| C2[Contact Details]
    C2 -->|Validate| C3[Operating Hours]
    C3 -->|Validate| C4[Social Media]

    D -->|Select| D1[Essential Pages]
    D1 --> D2[Menu & Dining]
    D2 --> D3[Gallery & Social]
    D3 --> D4[Business & Support]

    E -->|Customize| E1[Color Scheme]
    E1 --> E2[Typography]
    E2 --> E3[Preview Live]

    F -->|Review| F1[Generate Website]
    F1 --> F2[Show Preview]
    F2 -->|Success| F3[Download/Create New]
---
