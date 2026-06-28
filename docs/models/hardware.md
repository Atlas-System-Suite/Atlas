# Hardware Models

Hardware Models decouple physical pin manipulation from logical capabilities, allowing Atlas Managers to control robotics on a Raspberry Pi as easily as they control software logic.

---

## `atlas.hardware.gpio`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** General Purpose Input/Output pin control.

### Capabilities
- **`set_mode(pin: integer, mode: string) -> void`** (modes: "IN", "OUT")
- **`write(pin: integer, value: boolean) -> void`**
- **`read(pin: integer) -> boolean`**
- **`watch(pin: integer, edge: string, handler_capability: string) -> void`** (edges: "RISING", "FALLING", "BOTH")

---

## `atlas.hardware.motor`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** High-level motor and servo control.

### Capabilities
- **`set_speed(speed: float) -> void`** (-1.0 to 1.0)
- **`set_position(angle: float) -> void`**
- **`stop() -> void`**

---

## `atlas.hardware.serial`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** UART / Serial port communication.

### Capabilities
- **`open(port: string, baud_rate: integer) -> boolean`**
- **`write(data: bytes) -> void`**
- **`read(num_bytes: integer) -> bytes`**
- **`close() -> void`**

---

## `atlas.resource.gps_coordinate`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of a global position.

### Schema
```yaml
schema:
  type: object
  properties:
    latitude:
      type: float
    longitude:
      type: float
    altitude:
      type: float
    timestamp:
      type: float
```

---

## `atlas.resource.sensor_reading`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of raw sensor data (e.g., temperature, humidity).

### Schema
```yaml
schema:
  type: object
  properties:
    sensor_type:
      type: string
    value:
      type: float
    unit:
      type: string
```

---

## Other Planned Hardware Capabilities
- **PWM / I²C / SPI / CAN:** Low-level bus protocols.
- **Bluetooth / Wi-Fi:** Wireless interface control.
- **Encoder / IMU:** Hardware position and orientation feedback.
- **Display:** E-ink or LCD hardware screen controllers.
