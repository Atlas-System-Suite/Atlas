# Atlas Standard Models v1

Welcome to the **Atlas Standard Models** catalog. 

If the Standard Library is the vocabulary of Atlas, the Models are the grammar. They define the semantic contracts that allow Workers written in Python, Rust, or Go to communicate seamlessly without knowing about each other's existence.

---

## Philosophy

A Model is a **contract**, not an implementation. 

A Model defines:
- **Capabilities** (the public methods and expected inputs/outputs)
- **Events** (asynchronous notifications emitted by the implementation)
- **Errors** (expected failure states)
- **Configuration** (global settings required to operate)

A Model NEVER defines:
- **Programming language**
- **Transport mechanisms** (e.g., TCP vs Memory)
- **Serialization formats** (e.g., JSON vs Protobuf)

---

## Capability vs Resource Models

Atlas models are split into two distinct categories.

### 1. Capability Models (Verbs)
These define behavior. A Capability Model represents a service that does work (e.g., `atlas.storage`, `atlas.media.camera`). Workers *implement* Capability Models.

### 2. Resource Models (Nouns)
These define data structures. A Resource Model represents a canonical object flowing through the system (e.g., `atlas.resource.image`, `atlas.resource.gps_coordinate`). 

**Why separate them?**
The Translation Layer relies on Resource Models. If a Python UI Worker requests an image from a Rust Camera Worker, the two languages have completely different internal representations of an image. Because Atlas standardizes the `atlas.resource.image` schema, the Translator simply maps both languages to this canonical shape, ensuring perfect interoperability.

---

## The Catalog

Explore the official Capability and Resource models below:

### 1. [Core](core.md)
Foundational behaviors.
*Capabilities:* Logger, Configuration, Settings, Registry, Environment, Scheduler, Timer, Clock, Random, UUID, Resource, Lifecycle, Health.

### 2. [Storage](storage.md)
Data persistence and retrieval.
*Capabilities:* Storage, Filesystem, Database, Cache, Key-Value Store, Blob Storage, Configuration Store.
*Resources:* File.

### 3. [Networking](networking.md)
External connectivity.
*Capabilities:* HTTP Client, HTTP Server, TCP, UDP, WebSocket, MQTT, DNS, RPC, Transport.
*Resources:* HttpRequest, HttpResponse.

### 4. [Runtime](runtime.md)
Internal execution mechanics.
*Capabilities:* Worker Discovery, Session, Room, Invocation, Translation, Package, Update, Diagnostics.

### 5. [User Interface](ui.md)
Graphical and terminal interfaces.
*Capabilities:* Window, Workspace, Theme, Dialog, Notification, Clipboard, Terminal, Input.

### 6. [Media](media.md)
Audio, video, and image processing.
*Capabilities:* Image, Audio, Video, Camera, Microphone, Streaming.
*Resources:* Image, Audio Frame, Video Frame.

### 7. [AI](ai.md)
Machine learning and inference.
*Capabilities:* Inference, Embedding, Tokenizer, Prompt, Vector Store, Retrieval, Memory.
*Resources:* Tensor, EmbeddingVector, PromptTemplate.

### 8. [Hardware](hardware.md)
Physical devices and sensors.
*Capabilities:* GPIO, PWM, Serial, I²C, SPI, CAN, Bluetooth, Wi-Fi, Motor, Servo, Encoder, IMU, GPS, Camera, Sensor, Display.
*Resources:* GPS Coordinate, Motor Command, SensorReading.
