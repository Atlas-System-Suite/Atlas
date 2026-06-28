# Building Workers with Roles 👷‍♀️🎭

Welcome to the **Atlas Worker Construction Guide**! If you're here, you probably want to build a Worker. Or maybe you're just looking for a good time. Either way, you're in the right place. 🚀

In Atlas, **Workers** are the absolute, undeniable source of all business logic. They are the *only* thing that executes code. But not all Workers are created equal. Some like to store data, some like to talk to users, and some just like to sit in the corner and watch (we call those Observers 👀).

To help Atlas Studio (and your fellow developers) understand what a Worker actually *does*, we use **Roles**. Roles are metadata tags that don't change how the Runtime executes your code, but they fundamentally change how the ecosystem treats it.

Let's dive into the different kinds of Workers you can build, and what roles they should play!

---

## The App Worker (`role: [app]`) 📱

Ah, the App worker. The face of the operation. The frontend. The UI. 

An `App` worker is typically the entry point for your users. It doesn't usually provide capabilities to others; instead, it consumes them. It's the needy friend that constantly asks the Database for storage, and the Logger for attention.

### How to build one:
App workers are usually singletons. You don't want 5 copies of your UI fighting over the screen, do you? (Actually, maybe you do. I'm not here to judge your avant-garde UI design).

```yaml
# manifest.yaml
id: my.awesome.app
name: Awesome App
roles: [app, ui]

execution:
  policy: singleton # One UI to rule them all

communication:
  transports: [memory, tcp]

# Apps usually import capabilities, they rarely export them!
imports:
  - capability: atlas.core.storage
```

> **Pro Tip:** Keep your App workers purely focused on presentation. Don't secretly wire a database connection inside an App worker. If you do, Solon will find you. And it will be very disappointed. 😔

---

## The Database Worker (`role: [database]`) 💾

Data goes in, data (hopefully) comes out. 

Database workers are the reliable workhorses of Atlas. They take data from other workers and put it somewhere safe. They implement standard Models (like `StorageModel`), so nobody actually cares if you're using SQLite, Postgres, or saving bytes to a `/dev/null` blackhole.

### How to build one:
Database workers should almost always use a `singleton` or `pool` execution policy to avoid file locking nightmares.

```python
# worker.py
from atlas.core.storage.model import StorageModel

class SQLiteWorker(StorageModel):
    def __init__(self):
        # We 'trust' you'll commit to this setup.
        self.db = connect("my_database.db")
        
    def write(self, key: str, data: bytes):
        # DROP TABLE users; -- just kidding, please don't.
        pass
```

```yaml
# manifest.yaml
roles: [database, storage]
exports:
  - capability: atlas.core.storage
```

---

## The Translator Worker (`role: [translator]`) 🗣️

Have you ever tried to pass a Python dictionary directly into a Rust struct? It's like trying to fit a square peg into a spherical black hole. 

That's where **Translators** come in. They don't do business logic. They just take Format A, and aggressively mutate it into Format B. Atlas automatically discovers them and chains them together.

### How to build one:
Translators must declare `translations` in their manifest. They should be completely stateless. If your Translator has state, you're doing it wrong. Let it go. 🧘

```yaml
# manifest.yaml
roles: [translator, utility]

# We don't export capabilities. We export pure conversion!
translations:
  - source_format: python
    target_format: json
    cost: 1 # Because we're cheap and efficient
```

---

## The Observer Worker (`role: [observer]`, `[telemetry]`) 🕵️

Observers are like that one manager who joins the Zoom call, mutes their mic, turns off their camera, and just... watches. 

In Atlas, Observers bind to Rooms to read the Registry and trace Invocations, but they are structurally forbidden from modifying state. They are strictly read-only. This makes them perfect for logging, tracing, and metrics (like Miron!).

### How to build one:
To make an observer, you don't actually change the worker itself. The magic happens when the worker *binds* to a Room.

```python
# When binding a telemetry worker to a Room
room_manager.bind_worker(
    room_id="room_123", 
    worker_id="MironTelemetry", 
    role="profiler", 
    is_observer=True # 👈 The magic word
)
```

If an Observer tries to mutate state in the Room Registry, Atlas will immediately throw an `IllegalStateTransitionError`. No touching the thermostat! 🛑

---

---

## Using Standard Models (The "How-To" Guide) 🛠️

If you're building a Worker and you need to talk to the outside world, you should *always* program against a **Model**, never a concrete implementation. Think of Models as the USB-C ports of Atlas—everyone agrees on the shape, so you can plug in whatever brand you want.

We've built some foundational Models in the Standard Library (`stdlib/core/`). Here's how you use them!

### 1. The Logger Model (`atlas.core.logger`)
Need to print something without `print()`-ing like it's 1999? Use the Logger!

```python
from stdlib.core.logger.model import LoggerModel

class MyWorker:
    def __init__(self, logger: LoggerModel):
        self.logger = logger
        
    def do_work(self):
        # Pass context dictionaries to make debugging a breeze 🌬️
        self.logger.info("Doing some heavy lifting!", context={"weight": "100kg"})
        try:
            1 / 0
        except ZeroDivisionError as e:
            self.logger.error("Math is hard.", exc_info=str(e))
```

### 2. The Config Model (`atlas.core.config`)
Stop hardcoding API keys. Seriously. The Config Model lets you pull settings gracefully.

```python
from stdlib.core.config.model import ConfigModel

class SecureWorker:
    def __init__(self, config: ConfigModel):
        # We 'trust' you set this in your environment variables.
        self.api_key = config.get("SUPER_SECRET_KEY", default="guest")
        
        if config.has("DEBUG_MODE"):
            print("Debug mode activated! 🚨")
```

### 3. The Storage Model (`atlas.core.storage`)
Whether you're saving to a local disk, an S3 bucket, or a Raspberry Pi's SD card, the Storage Model keeps your logic blissfully unaware.

```python
from stdlib.core.storage.model import StorageModel

class NoteTakerWorker:
    def __init__(self, storage: StorageModel):
        self.storage = storage
        
    def save_note(self, title: str, content: str):
        # The model handles whether this goes to disk, SQL, or the cloud! ☁️
        self.storage.write(f"notes/{title}.txt", content)
        
    def read_note(self, title: str):
        if self.storage.exists(f"notes/{title}.txt"):
            # read() always returns bytes, so remember to decode!
            data = self.storage.read(f"notes/{title}.txt")
            return data.decode("utf-8") if data else None
```

### 4. The Clock Model (`atlas.core.clock`)
Time is a construct. But sometimes you just need to wait a few seconds.

```python
from stdlib.core.clock.model import ClockModel

class SleepyWorker:
    def __init__(self, clock: ClockModel):
        self.clock = clock
        
    def take_a_nap(self):
        start_time = self.clock.timestamp()
        print(f"Going to sleep at {self.clock.now()} 😴")
        
        self.clock.sleep(5.0) # Zzz...
        
        print(f"Woke up! I slept for {self.clock.timestamp() - start_time} seconds.")
```

---

## Wrapping Up 🎁

When building Workers, remember the golden rule: **Do one thing, and do it well.** 

If your Worker is tagged with `[app, database, translator, hardware, ai, kitchen_sink]`, it's not a Worker anymore. It's a monolith in disguise. Break it apart!

Now go forth, write some code, and may your capabilities always resolve on the first try! ✨
