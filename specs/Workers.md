# Workers

**Worker** is the ONLY executable primitive in the Atlas architecture.

Everything executable is a Worker. There is NO architectural distinction between "Applications", "Providers", or "Modules". 

## Examples of Workers
- SQLite (Storage Provider)
- Gemini (AI Provider)
- Journal (Stateful application feature)
- Calendar (Stateful application feature)
- Task Manager
- Life (Manager)

## Core Responsibilities
Atlas coordinates; **Workers own**.

Every Worker may:
- **Own State:** Workers manage their own business state and persistence.
- **Implement Models:** Workers implement the declarative behaviors defined in Models.
- **Export Capabilities:** Workers expose Services, Widgets, Commands, and Events.
- **Communicate:** Workers communicate directly with other Workers post-binding (Atlas does NOT broker messages).

## Independence
Workers are designed to be:
- **Independently Installable:** Discovered and loaded by the Atlas runtime.
- **Independently Testable:** Tested using generated mocks from Solon.
- **Independently Distributable:** Versioned and shipped as standalone packages.

## Resolution
Workers never import other Workers directly. Instead, they declare a dependency on a Capability (defined by a Model). The Atlas Runtime resolves that Capability to a matching Worker, negotiates permissions, establishes a Session, and returns a binding.

From that point on, the Workers communicate directly.
