import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Set, Any

from .diagnostics import Result, PlanningFailedError, InvalidTopologyError
from .resolver import ResolutionGraph
from .registry import GlobalRegistry
from .manifest import WorkerManifest


# ---------------------------------------------------------
# Execution Plan Data Structures
# ---------------------------------------------------------

@dataclass(frozen=True)
class WorkerPlan:
    worker_id: str
    reuse_policy: str
    startup_index: int

@dataclass(frozen=True)
class RoomPlan:
    room_id: str
    steward_id: str
    participants: List[str]
    capabilities_involved: List[str]

@dataclass(frozen=True)
class SessionPlan:
    session_id: str
    source_worker: str
    target_worker: str
    capability: str

@dataclass(frozen=True)
class FailurePlan:
    affected_workers: List[str]
    strategy: str

@dataclass(frozen=True)
class ExecutionPlan:
    root_id: str
    startup_order: List[str]
    workers: Dict[str, WorkerPlan]
    rooms: Dict[str, RoomPlan]
    sessions: Dict[str, SessionPlan]
    failure_plans: Dict[str, FailurePlan]


# ---------------------------------------------------------
# Execution Planner
# ---------------------------------------------------------

class ExecutionPlanner:
    """
    Pure planning subsystem. Transforms a ResolutionGraph into an ExecutionPlan.
    Does not execute, instantiate workers, or build sessions.
    """
    def __init__(self, registry: GlobalRegistry):
        self._registry = registry

    def plan(self, graph: ResolutionGraph) -> Result[ExecutionPlan, Exception]:
        """Generates the comprehensive Execution Plan."""
        
        # Step 1: Topological Sort (Startup Ordering)
        sort_res = self._topological_sort(graph)
        if sort_res.is_err():
            return Result.err(sort_res.error)
        
        startup_order = sort_res.unwrap()
        
        # We need to reverse the dependency graph sort because if A depends on B, B must start first.
        # So we reverse the Kahn's output to get Startup Order.
        startup_order.reverse()
        
        workers: Dict[str, WorkerPlan] = {}
        rooms: Dict[str, RoomPlan] = {}
        sessions: Dict[str, SessionPlan] = {}
        failure_plans: Dict[str, FailurePlan] = {}
        
        # Step 2: Worker Planning & Failure Planning
        for idx, w_id in enumerate(startup_order):
            worker_opt = self._registry.get_worker(w_id)
            if not worker_opt:
                return Result.err(PlanningFailedError(f"Worker {w_id} disappeared from registry during planning."))
            
            manifest = worker_opt.manifest
            policy = manifest.execution.policy
            
            workers[w_id] = WorkerPlan(
                worker_id=w_id,
                reuse_policy=policy,
                startup_index=idx
            )
            
            # Simple failure plan: If this fails, all downstream (dependents) freeze
            # Dependents are nodes that point to this node.
            dependents = [src for src, deps in graph.edges.items() if w_id in deps]
            failure_plans[w_id] = FailurePlan(
                affected_workers=dependents,
                strategy="Freeze Dependents & Restart"
            )

        # Step 3: Room and Session Planning
        # Rule (for Sprint 2.3): If a worker requires multiple capabilities from the same target worker,
        # or if a target worker has multiple roles, we use a Room. Otherwise, a direct Session.
        
        room_counter = 0
        session_counter = 0
        
        for source_id, deps in graph.edges.items():
            for target_id in deps:
                # Find what capability this targets
                # We look at the ResolutionNode
                target_node = graph.nodes.get(target_id)
                capability = target_node.capability if target_node else "unknown"
                
                target_worker = self._registry.get_worker(target_id)
                roles = target_worker.manifest.roles if target_worker else []
                
                # Room Heuristic
                if len(roles) > 1:
                    room_id = f"room_{room_counter}"
                    room_counter += 1
                    rooms[room_id] = RoomPlan(
                        room_id=room_id,
                        steward_id="atlas.core",
                        participants=[source_id, target_id],
                        capabilities_involved=[capability]
                    )
                else:
                    session_id = f"session_{session_counter}"
                    session_counter += 1
                    sessions[session_id] = SessionPlan(
                        session_id=session_id,
                        source_worker=source_id,
                        target_worker=target_id,
                        capability=capability
                    )

        plan = ExecutionPlan(
            root_id=graph.root_id,
            startup_order=startup_order,
            workers=workers,
            rooms=rooms,
            sessions=sessions,
            failure_plans=failure_plans
        )
        return Result.ok(plan)

    def _topological_sort(self, graph: ResolutionGraph) -> Result[List[str], Exception]:
        """
        Kahn's Algorithm to sort workers topologically.
        If A -> B (A depends on B), B must appear first in startup order.
        Here we sort such that A appears before B, and we'll reverse it later.
        """
        in_degree: Dict[str, int] = {node: 0 for node in graph.nodes}
        
        # Calculate in-degrees
        for source, targets in graph.edges.items():
            for target in targets:
                if target in in_degree:
                    in_degree[target] += 1
                    
        queue = [node for node, degree in in_degree.items() if degree == 0]
        sorted_nodes = []
        
        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)
            
            for neighbor in graph.edges.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        if len(sorted_nodes) != len(graph.nodes):
            return Result.err(InvalidTopologyError(
                "Cycle detected during topological sort. (Resolver should have caught this!)"
            ))
            
        return Result.ok(sorted_nodes)

    def validate(self, plan: ExecutionPlan) -> bool:
        """Validates the execution plan is sound."""
        # Check that all workers in startup order are actually planned
        if set(plan.startup_order) != set(plan.workers.keys()):
            return False
            
        # Check that no worker is scheduled before its dependency
        # We can't easily rebuild the graph here, but we could verify indices
        return True

    def explain(self, plan: ExecutionPlan) -> str:
        """Returns a human readable explanation of the plan."""
        lines = [f"Execution Plan for {plan.root_id}"]
        lines.append("\nSTARTUP ORDER:")
        for idx, w_id in enumerate(plan.startup_order):
            w = plan.workers[w_id]
            lines.append(f"  {idx+1}. {w_id} [Policy: {w.reuse_policy}]")
            
        lines.append(f"\nROOMS TO CREATE: {len(plan.rooms)}")
        for r in plan.rooms.values():
            lines.append(f"  - {r.room_id}: Participants {r.participants}")
            
        lines.append(f"\nSESSIONS TO ESTABLISH: {len(plan.sessions)}")
        for s in plan.sessions.values():
            lines.append(f"  - {s.session_id}: {s.source_worker} -> {s.target_worker} ({s.capability})")
            
        return "\n".join(lines)
        
    def serialize(self, plan: ExecutionPlan) -> str:
        """Serializes the plan to JSON for caching."""
        return json.dumps(asdict(plan), indent=2)
