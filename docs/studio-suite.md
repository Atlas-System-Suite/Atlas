# Atlas Studio Suite

The Atlas Studio Suite is the official developer toolkit and ecosystem for the Atlas platform. 

Atlas itself is just the execution model (the Runtime). To build, validate, and manage software effectively on Atlas, developers use the Studio Suite. The Suite is designed as an ecosystem of distinct tools, each handling a specific phase of the software lifecycle.

## Miron (Runtime Console)

**Miron** is the visual runtime console for Atlas. 
*(Conceptual equivalent: Task Manager + Docker Desktop + Runtime Inspector).*

**Responsibilities:**
- Inspect running Workers in real-time.
- Monitor Data Plane communication and Session health.
- View the active Registry (what Capabilities are bound to what).
- Visualize the runtime topology (dependency graphs).
- Pause, stop, and manage running Workers.

## Solon (The Toolchain)

**Solon** is the build system and static validator for Atlas.
*(Conceptual equivalent: The Rust `cargo` CLI + OpenAPI generators).*

**Responsibilities:**
- Validate Worker manifests against Model specifications.
- Generate test mocks for Capabilities.
- Generate Python SDKs and interface stubs from YAML Models.
- Validate architectural compliance without booting the Runtime.

*Example commands:*
- `solon build`
- `solon test sqlite`
- `solon validate`
- `solon docs`

## Varsity (The Mentor)

**Varsity** is the learning platform and scaffolding engine.
*(Conceptual equivalent: interactive tutorials + project generators).*

**Responsibilities:**
- Provide interactive tutorials on Atlas architecture.
- Scaffold new Workers and Models using best practices.
- Act as an architecture mentor, reviewing project structures.
- Recommend standard patterns and predefined Roles.

## Future Extensibility

The Studio Suite is not a single, monolithic application. It is an ecosystem. Future applications (like visual node-editors for routing Events, or marketplace managers) will fit naturally into this suite, leveraging the standardized Model format.
