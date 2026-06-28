from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import re

from .diagnostics import Result, AmbiguousResolutionError, CircularDependencyError, ResolutionFailedError
from .manifest import WorkerManifest
from .registry import GlobalRegistry

# ---------------------------------------------------------
# Semantic Versioning
# ---------------------------------------------------------

def match_version(provided_version: str, constraint: str) -> bool:
    """
    Language-agnostic lightweight SemVer matcher.
    Supports: exact, >=, ^
    """
    if not constraint or constraint == "*":
        return True

    # Parse provided version (e.g., "1.2.3")
    prov_parts = [int(x) for x in provided_version.split(".") if x.isdigit()]
    while len(prov_parts) < 3: prov_parts.append(0)

    # Parse constraint
    if constraint.startswith(">="):
        min_ver = constraint[2:]
        min_parts = [int(x) for x in min_ver.split(".") if x.isdigit()]
        while len(min_parts) < 3: min_parts.append(0)
        return prov_parts >= min_parts

    elif constraint.startswith("^"):
        # Compatible minor updates: ^1.2.0 means >=1.2.0 and <2.0.0
        # ^0.2.0 means >=0.2.0 and <0.3.0
        min_ver = constraint[1:]
        min_parts = [int(x) for x in min_ver.split(".") if x.isdigit()]
        while len(min_parts) < 3: min_parts.append(0)
        
        if prov_parts < min_parts:
            return False
            
        if min_parts[0] == 0:
            return prov_parts[0] == 0 and prov_parts[1] == min_parts[1]
        else:
            return prov_parts[0] == min_parts[0]

    else:
        # Exact match
        return provided_version == constraint


# ---------------------------------------------------------
# Resolution Graph Structures
# ---------------------------------------------------------

@dataclass(frozen=True)
class CapabilityMatch:
    worker_id: str
    version: str
    precedence: int

@dataclass(frozen=True)
class ResolutionNode:
    worker_id: str
    capability: str
    version: str
    is_optional: bool

@dataclass(frozen=True)
class ResolutionGraph:
    root_id: str
    nodes: Dict[str, ResolutionNode] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict) # worker_id -> list of dependency worker_ids
    missing_optionals: List[str] = field(default_factory=list)


# ---------------------------------------------------------
# Capability Resolver
# ---------------------------------------------------------

class CapabilityResolver:
    """
    Pure planning subsystem. Resolves dependency graphs by querying the Registry.
    Performs DFS with cycle detection and strict ambiguity checks.
    """
    def __init__(self, registry: GlobalRegistry):
        self._registry = registry

    def resolve(self, root_manifest: WorkerManifest) -> Result[ResolutionGraph, Exception]:
        """
        Resolves the entire dependency tree for the given manifest.
        """
        nodes: Dict[str, ResolutionNode] = {}
        edges: Dict[str, List[str]] = {}
        missing_optionals: List[str] = []
        
        # We trace paths to detect circular dependencies (e.g. A -> B -> A)
        path = set()

        res = self._dfs_resolve(
            manifest=root_manifest,
            capability_requested="root",
            is_optional=False,
            path=path,
            nodes=nodes,
            edges=edges,
            missing_optionals=missing_optionals
        )

        if res.is_err():
            return Result.err(res.error)

        graph = ResolutionGraph(
            root_id=root_manifest.id,
            nodes=nodes,
            edges=edges,
            missing_optionals=missing_optionals
        )
        return Result.ok(graph)

    def _dfs_resolve(self, manifest: WorkerManifest, capability_requested: str, is_optional: bool, 
                     path: Set[str], nodes: Dict[str, ResolutionNode], edges: Dict[str, List[str]], 
                     missing_optionals: List[str]) -> Result[None, Exception]:
        
        worker_id = manifest.id

        # Cycle Detection
        if worker_id in path:
            return Result.err(CircularDependencyError(
                f"Circular dependency detected at {worker_id}", 
                context={"path": str(list(path))}
            ))
            
        path.add(worker_id)
        
        # Record this node
        if worker_id not in nodes:
            nodes[worker_id] = ResolutionNode(
                worker_id=worker_id,
                capability=capability_requested,
                version=manifest.version,
                is_optional=is_optional
            )
            edges[worker_id] = []
            
        # Traverse dependencies
        for imp in manifest.imports:
            cap_name = imp.capability_name
            constraint = imp.version_requirement
            
            # Find providers in Registry
            providers_res = self._registry.find_providers_for_capability(cap_name)
            
            valid_matches: List[CapabilityMatch] = []
            if providers_res.is_ok():
                for p_id in providers_res.unwrap():
                    # Since we are planning, we need to inspect the provider's manifest
                    # The registry has the worker instance, which has the manifest
                    # We bypass locks since it's a synchronous graph build, but ideally we use a safe getter
                    provider_opt = self._registry.get_worker(p_id)
                    if provider_opt:
                        p_manifest = provider_opt.manifest
                        # Check version matching
                        for exp in p_manifest.exports:
                            if exp.capability_name == cap_name and match_version(exp.version, constraint):
                                valid_matches.append(CapabilityMatch(p_id, exp.version, exp.precedence))

            if not valid_matches:
                if imp.optional:
                    missing_optionals.append(cap_name)
                    continue
                else:
                    return Result.err(ResolutionFailedError(
                        f"Failed to resolve required capability: {cap_name} (Constraint: {constraint})",
                        context={"requested_by": worker_id}
                    ))

            # Sort matches by precedence descending
            valid_matches.sort(key=lambda x: x.precedence, reverse=True)
            
            # Ambiguity Check
            if len(valid_matches) > 1 and valid_matches[0].precedence == valid_matches[1].precedence:
                return Result.err(AmbiguousResolutionError(
                    f"Ambiguous resolution for {cap_name}. Multiple providers have equal precedence: {valid_matches[0].worker_id} and {valid_matches[1].worker_id}",
                    context={"requested_by": worker_id}
                ))
                
            chosen_match = valid_matches[0]
            edges[worker_id].append(chosen_match.worker_id)
            
            # Recurse into the chosen provider
            chosen_provider = self._registry.get_worker(chosen_match.worker_id)
            res = self._dfs_resolve(
                manifest=chosen_provider.manifest,
                capability_requested=cap_name,
                is_optional=imp.optional,
                path=path,
                nodes=nodes,
                edges=edges,
                missing_optionals=missing_optionals
            )
            
            if res.is_err():
                return res

        # Backtrack cycle path
        path.remove(worker_id)
        return Result.ok(None)

    def explain(self, graph: ResolutionGraph) -> str:
        """Returns a human-readable explanation of the resolution graph."""
        lines = [f"Resolution Graph for {graph.root_id}:"]
        
        def print_tree(node_id: str, depth: int):
            indent = "  " * depth
            node = graph.nodes[node_id]
            lines.append(f"{indent}↓ {node_id} (Provides: {node.capability} v{node.version})")
            for dep_id in graph.edges.get(node_id, []):
                print_tree(dep_id, depth + 1)
                
        print_tree(graph.root_id, 0)
        
        if graph.missing_optionals:
            lines.append("\nMissing Optional Capabilities:")
            for opt in graph.missing_optionals:
                lines.append(f"  - {opt}")
                
        return "\n".join(lines)
