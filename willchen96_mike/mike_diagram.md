graph TD
    Repo["📦 willchen96/mike"]

    Phase1["Phase 1: Understanding<br/>✅ 2 🟡 1 🔴 0"]
    Phase2["Phase 2: Structural<br/>✅ 0 🟡 1 🔴 0"]
    Phase3["Phase 3: Quality<br/>✅ 1 🟡 2 🔴 1"]
    Phase4["Phase 4: Security<br/>✅ 1 🟡 2 🔴 0"]

    Repo --> Phase1
    Repo --> Phase2
    Repo --> Phase3
    Repo --> Phase4

    classDef green fill:#90EE90
    classDef yellow fill:#FFD700
    classDef red fill:#FF6B6B
    classDef neutral fill:#E0E0E0
