import yaml
import os
import hashlib
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import threading

from .diagnostics import Result, ParseError, ValidationError

# ---------------------------------------------------------
# Immutable Data Structures
# ---------------------------------------------------------

@dataclass(frozen=True)
class ExecutionPolicy:
    policy: str

@dataclass(frozen=True)
class CommunicationPolicy:
    required_capabilities: List[str]
    optional_capabilities: List[str]
    default_format: str = "binary"

@dataclass(frozen=True)
class ImportDefinition:
    capability_name: str
    version_requirement: str
    optional: bool
    reason: str

@dataclass(frozen=True)
class ExportDefinition:
    capability_name: str
    version: str
    precedence: int = 0

@dataclass(frozen=True)
class TranslationDefinition:
    source_format: str
    target_format: str
    version_compat: str = "*"
    cost: int = 1

@dataclass(frozen=True)
class WorkerManifest:
    id: str
    name: str
    version: str
    language: str
    roles: List[str]
    
    execution: ExecutionPolicy
    communication: CommunicationPolicy
    
    imports: List[ImportDefinition]
    exports: List[ExportDefinition]
    translations: List[TranslationDefinition] = field(default_factory=list)

# ---------------------------------------------------------
# Readers-Writer Lock (RwLock) implementation
# ---------------------------------------------------------

class RwLock:
    """A simple Readers-Writer Lock to protect the cache from read starvation."""
    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    def acquire_read(self):
        self._read_ready.acquire()
        try:
            self._readers += 1
        finally:
            self._read_ready.release()

    def release_read(self):
        self._read_ready.acquire()
        try:
            self._readers -= 1
            if not self._readers:
                self._read_ready.notify_all()
        finally:
            self._read_ready.release()

    def acquire_write(self):
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self):
        self._read_ready.release()

# ---------------------------------------------------------
# Manifest Loader
# ---------------------------------------------------------

class ManifestLoader:
    def __init__(self):
        self._cache: Dict[str, WorkerManifest] = {}
        self._lock = RwLock()

    def get_cached(self, worker_id: str) -> Optional[WorkerManifest]:
        """Returns a cached manifest by Worker ID (Read Lock)."""
        self._lock.acquire_read()
        try:
            return self._cache.get(worker_id)
        finally:
            self._lock.release_read()

    def load_file(self, path: str) -> Result[WorkerManifest, Exception]:
        """Loads and validates a single manifest file."""
        if not os.path.exists(path):
            return Result.err(ParseError(f"File not found: {path}"))

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return Result.err(ParseError(f"YAML Syntax error: {e}", context={"file": path}))
        except Exception as e:
            return Result.err(ParseError(f"I/O error: {e}", context={"file": path}))

        # Schema Validation
        if not isinstance(data, dict):
            return Result.err(ValidationError("Manifest must be a YAML dictionary", context={"file": path}))

        worker_data = data.get("worker")
        if not worker_data:
            return Result.err(ValidationError("Missing 'worker' block", context={"file": path}))
        
        required_fields = ["id", "name", "version", "language", "roles"]
        for field in required_fields:
            if field not in worker_data:
                return Result.err(ValidationError(f"Missing required field: {field}", context={"file": path}))
        
        if not isinstance(worker_data.get("roles"), list):
            return Result.err(ValidationError("Roles must be a list", context={"file": path}))

        exec_data = data.get("execution", {"policy": "singleton"})
        comm_data = data.get("communication", {"transports": [], "serialization": []})

        # Hydrate structs
        try:
            execution = ExecutionPolicy(policy=exec_data.get("policy", "singleton"))
            communication = CommunicationPolicy(
                required_capabilities=comm_data.get("requires", []),
                optional_capabilities=comm_data.get("optional", []),
                default_format=comm_data.get("default_format", "binary")
            )

            imports = []
            for imp in data.get("imports", {}).get("capabilities", []):
                imports.append(ImportDefinition(
                    capability_name=imp.get("name", ""),
                    version_requirement=imp.get("version", ""),
                    optional=imp.get("optional", False),
                    reason=imp.get("reason", "")
                ))

            exports = []
            for exp in data.get("exports", {}).get("capabilities", []):
                exports.append(ExportDefinition(
                    capability_name=exp.get("name", ""),
                    version=exp.get("version", ""),
                    precedence=exp.get("precedence", 0)
                ))
                
            translations = []
            for trans in data.get("translations", []):
                translations.append(TranslationDefinition(
                    source_format=trans.get("source_format", ""),
                    target_format=trans.get("target_format", ""),
                    version_compat=trans.get("version_compat", "*"),
                    cost=trans.get("cost", 1)
                ))

            manifest = WorkerManifest(
                id=data.get("id", ""),
                name=data.get("name", ""),
                version=data.get("version", ""),
                language=data.get("language", ""),
                roles=data.get("roles", []),
                execution=execution,
                communication=communication,
                imports=imports,
                exports=exports,
                translations=translations
            )
        except Exception as e:
            return Result.err(ValidationError(f"Hydration failed: {e}", context={"file": path}))

        # Caching (Write Lock)
        self._lock.acquire_write()
        try:
            self._cache[manifest.id] = manifest
        finally:
            self._lock.release_write()

        return Result.ok(manifest)

    def load_directory(self, path: str) -> Result[List[WorkerManifest], ParseError]:
        """Loads all worker.yaml files in a directory."""
        if not os.path.exists(path) or not os.path.isdir(path):
            return Result.err(ParseError(f"Directory not found: {path}"))

        manifests = []
        for root, _, files in os.walk(path):
            if "worker.yaml" in files:
                file_path = os.path.join(root, "worker.yaml")
                res = self.load_file(file_path)
                if res.is_err():
                    return Result.err(res.error) # Fail-fast on invalid manifest
                manifests.append(res.unwrap())
        
        return Result.ok(manifests)
