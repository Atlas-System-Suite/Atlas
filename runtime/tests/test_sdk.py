from typing import Any
import pytest
from atlas_sdk import WorkerBase, capability, on_invocation, require
from atlas_sdk.testing import MockRuntime


def test_require_decorator_metadata():
    @require("atlas.core.logger", version="^1.0.0", as_alias="log")
    class TestReqWorker(WorkerBase):
        _worker_id = "test.req_worker"
        
        def on_init(self):
            pass

    worker = TestReqWorker()
    meta = worker.get_meta()
    
    assert len(meta.requirements) == 1
    assert meta.requirements[0]["capability"] == "atlas.core.logger"
    assert meta.requirements[0]["version"] == "^1.0.0"
    assert meta.requirements[0]["as_alias"] == "log"
    
    # Verify manifest generation
    manifest = worker.generate_manifest()
    assert len(manifest["imports"]) == 1
    assert manifest["imports"][0]["capability"] == "atlas.core.logger"
    assert manifest["imports"][0]["version"] == "^1.0.0"


@pytest.mark.asyncio
async def test_require_mock_injection():
    # 1. Define capability provider
    class ProviderWorker(WorkerBase):
        _worker_id = "test.provider"
        
        @capability("atlas.core.logger", version="1.0.0")
        @on_invocation("write_log")
        def write_log(self, message: str) -> str:
            return f"LOGGED: {message}"

    # 2. Define capability consumer using @require
    class ConsumerWorker(WorkerBase):
        _worker_id = "test.consumer"
        
        @require("atlas.core.logger", version="1.0.0", as_alias="log")
        def on_init(self):
            pass

        @capability("test.consumer.run", version="1.0.0")
        @on_invocation("run")
        async def run(self, msg: str) -> str:
            # Invokes required capability via proxy
            res = await self.log.write_log(message=msg)
            return f"Consumer got: {res}"

    # 3. Register both in MockRuntime
    runtime = MockRuntime()
    runtime.register(ProviderWorker)
    consumer = runtime.register(ConsumerWorker)
    
    # Verify the proxy was injected
    assert hasattr(consumer, "log")
    
    # 4. Invoke consumer and check routing
    result = await runtime.invoke("test.consumer", "run", {"msg": "hello"})
    assert result == "Consumer got: LOGGED: hello"
