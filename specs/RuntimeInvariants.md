A Worker never owns another Worker.

A Room never owns business state.

Atlas never executes business logic.

Every Worker is discoverable through the Registry.

Every Session belongs to exactly one Room.

Every Invocation belongs to exactly one Session.

Every runtime decision is explainable from metadata.

Workers never communicate without Atlas-mediated session establishment.

The Global Registry stores facts, not application data.