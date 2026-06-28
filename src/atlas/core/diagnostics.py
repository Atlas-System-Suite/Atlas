from enum import Enum
from typing import Dict, Generic, TypeVar, Optional, Any
from dataclasses import dataclass, field

class Severity(Enum):
    FATAL = "Fatal"
    RECOVERABLE = "Recoverable"
    WARNING = "Warning"


@dataclass(frozen=True)
class AtlasError(Exception):
    """Base error class for all structured Atlas errors."""
    code: str
    severity: Severity
    message: str
    context: Dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.severity.value}] {self.code}: {self.message} | Context: {self.context}"


class ParseError(AtlasError):
    """Raised when a manifest file has invalid syntax."""
    def __init__(self, message: str, context: Optional[Dict[str, str]] = None):
        super().__init__(code="ERR_PARSE_INVALID", severity=Severity.FATAL, message=message, context=context or {})


class ValidationError(AtlasError):
    """Raised when a manifest fails schema validation."""
    def __init__(self, message: str, context: Optional[Dict[str, str]] = None):
        super().__init__(code="ERR_VALIDATION_FAILED", severity=Severity.FATAL, message=message, context=context or {})


class LoadError(AtlasError):
    """Raised when an OS-level dynamic loading failure occurs."""
    def __init__(self, message: str, context: Optional[Dict[str, str]] = None):
        super().__init__(code="ERR_LOAD_FAILED", severity=Severity.FATAL, message=message, context=context or {})


class MissingSymbolError(AtlasError):
    """Raised when a loaded module lacks required exported interfaces."""
    def __init__(self, message: str, context: Optional[Dict[str, str]] = None):
        super().__init__(code="ERR_MISSING_SYMBOL", severity=Severity.FATAL, message=message, context=context or {})


class IdCollisionError(AtlasError):
    """Raised when a Worker ID already exists in the Registry."""
    def __init__(self, message: str, context: Optional[Dict[str, str]] = None):
        super().__init__(code="ERR_ID_COLLISION", severity=Severity.RECOVERABLE, message=message, context=context or {})


class LookupError(AtlasError):
    """Raised when a capability lookup fails."""
    def __init__(self, message: str, context: Optional[Dict[str, str]] = None):
        super().__init__(code="ERR_LOOKUP_FAILED", severity=Severity.RECOVERABLE, message=message, context=context or {})


class IllegalStateTransitionError(AtlasError):
    """Raised when a Worker attempts an invalid lifecycle transition."""
    def __init__(self, message: str, context: Optional[Dict[str, str]] = None):
        super().__init__(code="ERR_ILLEGAL_STATE_TRANSITION", severity=Severity.FATAL, message=message, context=context or {})



# ---------------------------------------------------------
# Result Type (Rust-style error boundaries)
# ---------------------------------------------------------

T = TypeVar('T')
E = TypeVar('E', bound=AtlasError)

@dataclass(frozen=True)
class Result(Generic[T, E]):
    """
    A Rust-like Result type to enforce strict error handling boundaries.
    Subsystems should return Result objects instead of raising exceptions across boundaries.
    """
    value: Optional[T] = None
    error: Optional[E] = None

    @classmethod
    def ok(cls, value: T) -> "Result[T, E]":
        return cls(value=value, error=None)

    @classmethod
    def err(cls, error: E) -> "Result[T, E]":
        return cls(value=None, error=error)

    def is_ok(self) -> bool:
        return self.error is None

    def is_err(self) -> bool:
        return self.error is not None

    def unwrap(self) -> T:
        if self.is_err():
            # If a developer unrwaps an error, it escalates to a Python crash.
            # This should only be used when they are 100% sure it is OK.
            raise self.error
        return self.value

