# AI Models

AI Models standardize the interface to Large Language Models (LLMs), embeddings, and semantic databases, allowing a Manager to swap between a local model and a cloud API trivially.

---

## `atlas.ai.inference`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Generates text or actions from an LLM.

### Capabilities
- **`generate(prompt: atlas.resource.prompt_template, max_tokens: integer) -> string`**
- **`stream(prompt: atlas.resource.prompt_template) -> iter[string]`**

---

## `atlas.ai.embedding`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Converts text into numerical vectors for semantic search.

### Capabilities
- **`embed(text: string) -> atlas.resource.embedding_vector`**
- **`embed_batch(texts: list[string]) -> list[atlas.resource.embedding_vector]`**

---

## `atlas.ai.vector_store`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Specialized storage for semantic similarity search.

### Capabilities
- **`upsert(id: string, vector: atlas.resource.embedding_vector, metadata: dict) -> void`**
- **`search(vector: atlas.resource.embedding_vector, top_k: integer) -> list[dict]`**

---

## `atlas.resource.tensor`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of an N-dimensional mathematical tensor.

### Schema
```yaml
schema:
  type: object
  properties:
    shape:
      type: list[integer]
      description: "Dimensions of the tensor (e.g., [1, 28, 28])."
    data_type:
      type: string
      description: "e.g., float32, int8."
    raw_bytes:
      type: bytes
      description: "The flattened numerical data."
```

---

## `atlas.resource.embedding_vector`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of an embedding (specifically a 1D tensor).

### Schema
```yaml
schema:
  type: object
  properties:
    dimensions:
      type: integer
    values:
      type: list[float]
```

---

## `atlas.resource.prompt_template`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of an LLM prompt containing system and user messages.

### Schema
```yaml
schema:
  type: object
  properties:
    system_instruction:
      type: string
    messages:
      type: list[dict]
      description: "List of role/content pairs."
    temperature:
      type: float
```

---

## Other Planned AI Capabilities
- **Tokenizer:** For counting and encoding tokens locally to prevent API quota exhaustion.
- **Retrieval:** RAG (Retrieval-Augmented Generation) orchestrators.
- **Memory:** Context summarization and rolling buffers for conversational AI.
