"""Smart caching for the EMS data pipeline.

Tracks file hashes of raw inputs so that processing steps can be
skipped when the inputs have not changed since the last run.

Cache manifest is stored at:
    data/processed/.cache_manifest.json

Usage
-----
    from scripts.data_processing.cache import CacheManager
    cm = CacheManager(project_root)
    if cm.is_valid("tier2_crashes"):
        print("Using cached data")
    else:
        # ... regenerate ...
        cm.update("tier2_crashes")
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional


def compute_file_hash(path: Path, algorithm: str = "sha256", chunk_size: int = 8192) -> str:
    """Compute hex digest of a file using the given hash algorithm."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# Mapping: tier name -> (input glob patterns relative to project root, output files)
TIER_DEPENDENCIES: Dict[str, Dict] = {
    "tier1_boundaries": {
        "inputs": [
            "data/raw/manhattan_boundary.geojson",
            "data/raw/cbd_boundary.geojson",
        ],
        "outputs": [
            "data/processed/cache/manhattan_geom.pkl",
            "data/processed/cache/cbd_geom.pkl",
        ],
    },
    "tier2_firehouses": {
        "inputs": [
            "data/raw/FDNY_Firehouse_Listing_*.csv",
            "data/processed/cache/manhattan_geom.pkl",
            "data/processed/cache/cbd_geom.pkl",
        ],
        "outputs": [
            "data/processed/firehouses_clean.csv",
            "data/processed/firehouses_manhattan.csv",
        ],
    },
    "tier2_precincts": {
        "inputs": [
            "data/raw/Police_Precincts_*.csv",
            "data/processed/cache/manhattan_geom.pkl",
        ],
        "outputs": [
            "data/processed/precincts_manhattan.geojson",
        ],
    },
    "tier2_crashes": {
        "inputs": [
            "data/raw/Motor_Vehicle_Collisions_-_Crashes_*.csv",
            "data/processed/cache/manhattan_geom.pkl",
            "data/processed/cache/cbd_geom.pkl",
        ],
        "outputs": [
            "data/processed/crashes_manhattan.csv",
            "data/processed/crashes_manhattan.parquet",
        ],
    },
    "tier3_demand": {
        "inputs": [
            "data/processed/crashes_manhattan.parquet",
            "data/processed/precincts_manhattan.geojson",
        ],
        "outputs": [
            "data/processed/demand_lambda_hourly.csv",
            "data/processed/demand_lambda_dow.csv",
            "data/processed/demand_lambda_precinct.csv",
            "data/processed/demand_model_summary.json",
        ],
    },
    "tier3_distance": {
        "inputs": [
            "data/processed/firehouses_manhattan.csv",
            "data/processed/precincts_manhattan.geojson",
        ],
        "outputs": [
            "data/processed/distance_matrix_firehouse_precinct.csv",
            "data/processed/distance_matrix_firehouse_precinct_manhattan.csv",
        ],
    },
}


class CacheManager:
    """Manages a cache manifest that tracks input file hashes per tier."""

    def __init__(self, project_root: Path | str):
        self.project_root = Path(project_root)
        self.manifest_path = self.project_root / "data" / "processed" / ".cache_manifest.json"
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_manifest(self) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump(self._manifest, f, indent=2)

    def _resolve_inputs(self, tier_name: str) -> List[Path]:
        """Resolve glob patterns to actual file paths for a tier."""
        dep = TIER_DEPENDENCIES.get(tier_name)
        if dep is None:
            return []
        paths = []
        for pattern in dep["inputs"]:
            p = Path(pattern)
            if "*" in pattern:
                matches = sorted(self.project_root.glob(pattern))
                paths.extend(matches)
            else:
                full = self.project_root / pattern
                if full.exists():
                    paths.append(full)
        return paths

    def _compute_hashes(self, tier_name: str) -> Dict[str, str]:
        """Compute hashes of all input files for a tier."""
        hashes = {}
        for path in self._resolve_inputs(tier_name):
            rel = str(path.relative_to(self.project_root))
            hashes[rel] = compute_file_hash(path)
        return hashes

    def _outputs_exist(self, tier_name: str) -> bool:
        """Check that all output files for a tier exist."""
        dep = TIER_DEPENDENCIES.get(tier_name)
        if dep is None:
            return True
        for out_path in dep["outputs"]:
            if not (self.project_root / out_path).exists():
                return False
        return True

    def is_valid(self, tier_name: str) -> bool:
        """Check if cached outputs are still valid for a given tier.

        Returns True if all inputs have the same hash as the last
        successful run AND all output files exist.
        """
        if not self._outputs_exist(tier_name):
            return False

        cached = self._manifest.get(tier_name, {}).get("input_hashes", {})
        if not cached:
            return False

        current = self._compute_hashes(tier_name)
        return current == cached

    def update(self, tier_name: str) -> None:
        """Record current input hashes after a successful processing run."""
        self._manifest[tier_name] = {
            "input_hashes": self._compute_hashes(tier_name),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self._save_manifest()

    def invalidate(self, tier_name: Optional[str] = None) -> None:
        """Remove cache entries.  If tier_name is None, clear all."""
        if tier_name is None:
            self._manifest = {}
        else:
            self._manifest.pop(tier_name, None)
        self._save_manifest()

    def summary(self) -> str:
        """Return a human-readable summary of cache state."""
        lines = ["Cache status:"]
        for tier in TIER_DEPENDENCIES:
            valid = self.is_valid(tier)
            ts = self._manifest.get(tier, {}).get("timestamp", "never")
            status = "valid" if valid else "stale/missing"
            lines.append(f"  {tier:25s}  {status:15s}  (last: {ts})")
        return "\n".join(lines)
