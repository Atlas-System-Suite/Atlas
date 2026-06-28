# Networking Models

Networking Models abstract external communication protocols.

---

## `atlas.network.http_client`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Fetches data from remote REST APIs.

### Capabilities
- **`request(method: string, url: string, headers: dict, body: string) -> atlas.resource.http_response`**
- **`get(url: string) -> atlas.resource.http_response`**
- **`post(url: string, body: string) -> atlas.resource.http_response`**

---

## `atlas.network.http_server`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Serves incoming HTTP requests.

### Capabilities
- **`start(port: integer) -> void`**
- **`stop() -> void`**
- **`register_route(method: string, path: string, handler_capability: string) -> void`**

### Events
- `server_started` (port: integer)
- `server_stopped` ()

---

## `atlas.network.websocket`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Full-duplex communication channel.

### Capabilities
- **`connect(url: string) -> boolean`**
- **`send(message: string) -> void`**
- **`on_message(handler_capability: string) -> void`**

---

## `atlas.resource.http_request`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of an HTTP Request.

### Schema
```yaml
schema:
  type: object
  properties:
    method:
      type: string
    url:
      type: string
    headers:
      type: dict
    body:
      type: string
    source_ip:
      type: string
```

---

## `atlas.resource.http_response`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of an HTTP Response.

### Schema
```yaml
schema:
  type: object
  properties:
    status_code:
      type: integer
    headers:
      type: dict
    body:
      type: string
```

---

## Other Planned Networking Capabilities
- **TCP / UDP:** Raw socket connections.
- **MQTT:** Pub/sub messaging for IoT.
- **DNS:** Domain name resolution.
- **RPC:** Abstract remote procedure call layer (over HTTP or gRPC).
- **Transport:** Models for defining custom physical layer transports (e.g., CAN bus to IP bridges).
