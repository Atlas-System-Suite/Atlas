# Architecture

```mermaid
graph TD
    Lang[Programming Language] --> Runtime[Atlas Runtime]
    Runtime --> Workers[Workers]
    Workers --> Managers[Managers]
```
