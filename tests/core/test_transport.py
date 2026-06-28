import pytest
import threading
import time

from atlas.core.transport import InMemoryTransport, TransportPayload, TransportError

# ---------------------------------------------------------
# Step 3: Unit Tests
# ---------------------------------------------------------
def test_send_to_unregistered_listener():
    transport = InMemoryTransport()
    payload = TransportPayload(source_id="workerA", target_id="workerB", data=b"hello")
    
    res = transport.send(payload)
    assert res.is_err()
    assert isinstance(res.error, TransportError)
    
    transport.shutdown()

def test_successful_delivery():
    transport = InMemoryTransport()
    
    received_data = None
    event = threading.Event()
    
    def on_receive(payload: TransportPayload):
        nonlocal received_data
        received_data = payload.data
        event.set()
        
    transport.register_listener("workerB", on_receive)
    
    payload = TransportPayload(source_id="workerA", target_id="workerB", data=b"atlas-v1")
    res = transport.send(payload)
    assert res.is_ok()
    
    # Wait for the async dispatcher thread
    event.wait(timeout=1.0)
    assert received_data == b"atlas-v1"
    
    transport.shutdown()

def test_deregister_listener():
    transport = InMemoryTransport()
    transport.register_listener("workerB", lambda p: None)
    
    res = transport.send(TransportPayload("A", "B", b"test"))
    assert res.is_ok()
    
    transport.deregister_listener("workerB")
    
    res = transport.send(TransportPayload("A", "B", b"test"))
    assert res.is_err()
    
    transport.shutdown()

# ---------------------------------------------------------
# Step 4: Integration & Concurrency Tests
# ---------------------------------------------------------
def test_concurrent_senders():
    """10 workers sending bytes to a single receiver simultaneously."""
    transport = InMemoryTransport()
    
    received_count = 0
    lock = threading.Lock()
    event = threading.Event()
    
    def on_receive(payload: TransportPayload):
        nonlocal received_count
        with lock:
            received_count += 1
            if received_count == 100:
                event.set()
                
    transport.register_listener("server", on_receive)
    
    def worker_send():
        for _ in range(10):
            transport.send(TransportPayload("client", "server", b"msg"))
            
    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker_send)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    event.wait(timeout=2.0)
    assert received_count == 100
    
    transport.shutdown()

# ---------------------------------------------------------
# Step 5: Stress Tests
# ---------------------------------------------------------
def test_high_throughput():
    """Testing 10,000 messages pushed through the queue rapidly."""
    transport = InMemoryTransport()
    
    received = []
    event = threading.Event()
    
    def on_receive(payload: TransportPayload):
        received.append(payload)
        if len(received) == 10000:
            event.set()
            
    transport.register_listener("sink", on_receive)
    
    for i in range(10000):
        transport.send(TransportPayload("source", "sink", b"x"))
        
    # Give it up to 3 seconds to process 10k messages
    success = event.wait(timeout=3.0)
    assert success, f"Only received {len(received)} / 10000 messages"
    
    transport.shutdown()
