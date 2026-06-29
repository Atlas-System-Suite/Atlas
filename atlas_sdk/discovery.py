import os
import yaml
from typing import Optional, Dict, Any, List

class DiscoveryEngine:
    """
    Crawls the workspace to discover Atlas artifacts by locating `atlas.yaml`.
    """
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def find_manager_by_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """
        Walks the directory structure looking for an atlas.yaml of kind: manager
        where the requested alias is in its aliases list.
        """
        for root, dirs, files in os.walk(self.root_dir):
            # Skip non-Atlas directories
            if any(ignore in root for ignore in [".git", "__pycache__", ".pytest_cache", "venv", "dist", "scratch"]):
                continue

            if "atlas.yaml" in files:
                file_path = os.path.join(root, "atlas.yaml")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception:
                    continue
                
                if not isinstance(data, dict):
                    continue

                if data.get("kind") in ("manager", "suite"):
                    # Check aliases
                    aliases = data.get("aliases", [])
                    if alias in aliases:
                        return {
                            "path": root,
                            "manifest": data
                        }
        return None

    def find_worker(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """
        Walks the directory structure looking for an atlas.yaml of kind: worker
        where the requested id matches.
        """
        for root, dirs, files in os.walk(self.root_dir):
            if any(ignore in root for ignore in [".git", "__pycache__", ".pytest_cache", "venv", "dist", "scratch"]):
                continue

            if "atlas.yaml" in files:
                file_path = os.path.join(root, "atlas.yaml")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception:
                    continue
                
                if not isinstance(data, dict):
                    continue

                if data.get("kind") == "worker" and data.get("id") == worker_id:
                    return {
                        "path": root,
                        "manifest_path": file_path,
                        "manifest": data
                    }
        return None

    def list_managers(self) -> List[Dict[str, Any]]:
        results = []
        for root, dirs, files in os.walk(self.root_dir):
            if any(ignore in root for ignore in [".git", "__pycache__", ".pytest_cache", "venv", "dist", "scratch"]):
                continue

            if "atlas.yaml" in files:
                file_path = os.path.join(root, "atlas.yaml")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception:
                    continue
                
                if isinstance(data, dict) and data.get("kind") in ("manager", "suite"):
                    results.append({"path": root, "manifest": data})
        return results

    def list_workers(self) -> List[Dict[str, Any]]:
        results = []
        for root, dirs, files in os.walk(self.root_dir):
            if any(ignore in root for ignore in [".git", "__pycache__", ".pytest_cache", "venv", "dist", "scratch"]):
                continue

            if "atlas.yaml" in files:
                file_path = os.path.join(root, "atlas.yaml")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception:
                    continue
                
                if isinstance(data, dict):
                    # Check for flat or nested worker manifest
                    if data.get("kind") == "worker":
                        results.append({"path": root, "manifest": data})
                    elif data.get("worker"):
                        results.append({"path": root, "manifest": data.get("worker")})
        return results
