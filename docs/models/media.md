# Media Models

Media Models define operations on high-density data formats like images and audio, and provide the canonical Resource Models for translating them.

---

## `atlas.media.image`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Image manipulation and conversion.

### Capabilities
- **`resize(image: atlas.resource.image, width: integer, height: integer) -> atlas.resource.image`**
- **`crop(image: atlas.resource.image, x: integer, y: integer, width: integer, height: integer) -> atlas.resource.image`**
- **`convert(image: atlas.resource.image, format: string) -> atlas.resource.image`**

---

## `atlas.media.camera`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Interfaces with hardware cameras.

### Capabilities
- **`capture_frame() -> atlas.resource.video_frame`**
- **`start_stream(fps: integer) -> void`**
- **`stop_stream() -> void`**

### Events
- `frame_ready` (frame: atlas.resource.video_frame)

---

## `atlas.resource.image`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of an image.

### Schema
```yaml
schema:
  type: object
  properties:
    width:
      type: integer
    height:
      type: integer
    channels:
      type: integer
      description: "e.g., 3 for RGB, 4 for RGBA."
    color_space:
      type: string
    raw_bytes:
      type: bytes
      description: "Uncompressed pixel data."
```

---

## `atlas.resource.audio_frame`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of a chunk of audio.

### Schema
```yaml
schema:
  type: object
  properties:
    sample_rate:
      type: integer
    channels:
      type: integer
    bit_depth:
      type: integer
    raw_bytes:
      type: bytes
```

---

## Other Planned Media Capabilities
- **Microphone:** Audio capture model emitting `audio_frame` resources.
- **Audio / Video Playback:** For rendering media out to the host system.
- **Streaming:** Abstracting protocols like WebRTC or RTSP.
