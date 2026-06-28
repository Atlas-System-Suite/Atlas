# UI Models

UI Models standardize interactions with graphical desktop environments, terminal interfaces, and user input.

---

## `atlas.ui.window`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Manages native OS graphical windows.

### Capabilities
- **`create(title: string, width: integer, height: integer) -> string`** (Returns Window ID)
- **`show(window_id: string) -> void`**
- **`close(window_id: string) -> void`**
- **`render(window_id: string, layout: dict) -> void`**

### Events
- `window_closed` (window_id: string)
- `window_resized` (window_id: string, width: integer, height: integer)

---

## `atlas.ui.dialog`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Triggers native OS modal dialogs.

### Capabilities
- **`alert(title: string, message: string) -> void`**
- **`confirm(title: string, message: string) -> boolean`**
- **`prompt(title: string, message: string, default: string) -> string`**

---

## `atlas.ui.clipboard`

**Type:** Capability Model
**Version:** `1.0.0`
**Description:** Interacts with the system clipboard.

### Capabilities
- **`copy(text: string) -> boolean`**
- **`paste() -> string`**

---

## `atlas.resource.keyboard_event`

**Type:** Resource Model
**Version:** `1.0.0`
**Description:** Canonical representation of a keyboard keystroke.

### Schema
```yaml
schema:
  type: object
  properties:
    key:
      type: string
    code:
      type: integer
    modifiers:
      type: list[string] # e.g. ["ctrl", "shift"]
    is_repeat:
      type: boolean
```

---

## Other Planned UI Capabilities
- **Workspace:** Managing MDI (Multiple Document Interface) or tabbed layouts.
- **Theme:** Exposing system-level Light/Dark mode preferences.
- **Notification:** Triggering native OS toast notifications.
- **Terminal:** Rendering advanced CLI constructs (tables, progress bars) outside of standard logging.
- **Input:** Standardized mouse and touch events.
