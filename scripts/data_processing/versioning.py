"""Data versioning for the EMS optimization pipeline.

Tracks metadata for each data generation run, enabling
reproducibility and lineage tracking.

Manifest stored at:
    data/processed/.data_manifest.json

Usage
-----
    from scripts.data_processing.versioning import DataVersionManager
    dvm = DataVersionManager(project_root)
    dvm.create_manifest(seed=42)
    print(dvm.current_version())
"""
from __future__ import annotations

import datetime
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from scripts.data_processing.cache import compute_file_hash


def get_git_commit(project_root: Path) -> Optional[str]:
    """Return current git commit hash, or None if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def get_git_dirty(project_root: Path) -> Optional[bool]:
    """Return True if working tree has uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return len(result.stdout.strip()) > 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def get_software_versions() -> Dict[str, str]:
    """Return versions of key packages used in the pipeline."""
    versions = {
        "python": platform.python_version(),
    }
    for pkg in ["pandas", "numpy", "geopandas", "scipy", "shapely", "tqdm", "joblib"]:
        try:
            mod = __import__(pkg)
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            versions[pkg] = "not installed"
    return versions


def _get_raw_file_hashes(project_root: Path) -> Dict[str, str]:
    """Compute hashes of all raw data files."""
    raw_dir = project_root / "data" / "raw"
    hashes = {}
    if raw_dir.exists():
        for p in sorted(raw_dir.iterdir()):
            if p.is_file() and p.suffix in (".csv", ".geojson", ".xlsx"):
                try:
                    hashes[p.name] = compute_file_hash(p)
                except OSError:
                    hashes[p.name] = "error"
    return hashes


class DataVersionManager:
    """Manages data generation manifests for reproducibility."""

    def __init__(self, project_root: Path | str):
        self.project_root = Path(project_root)
        self.manifest_path = (
            self.project_root / "data" / "processed" / ".data_manifest.json"
        )

    def create_manifest(
        self,
        seed: Optional[int] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete manifest for the current data generation run."""
        manifest = {
            "version": "1.0",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "git_commit": get_git_commit(self.project_root),
            "git_dirty": get_git_dirty(self.project_root),
            "seed": seed,
            "software_versions": get_software_versions(),
            "raw_file_hashes": _get_raw_file_hashes(self.project_root),
            "platform": {
                "system": platform.system(),
                "machine": platform.machine(),
                "python_path": sys.executable,
            },
        }
        if extra_metadata:
            manifest["extra"] = extra_metadata

        # Save
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return manifest

    def load_manifest(self) -> Optional[Dict[str, Any]]:
        """Load existing manifest, or None if not found."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def current_version(self) -> str:
        """Return a concise version string from the current manifest."""
        m = self.load_manifest()
        if m is None:
            return "No manifest found. Run the pipeline to generate one."
        ts = m.get("generated_at", "unknown")
        commit = m.get("git_commit", "unknown")
        if commit and len(commit) > 8:
            commit = commit[:8]
        seed = m.get("seed", "unknown")
        return f"Generated: {ts} | Commit: {commit} | Seed: {seed}"

    def compare_manifests(
        self, other: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compare current state vs saved manifest to check if regeneration needed.

        Returns a dict with:
            needs_regeneration: bool
            reasons: list of strings
        """
        current_manifest = self.load_manifest()
        if current_manifest is None:
            return {
                "needs_regeneration": True,
                "reasons": ["No existing manifest found."],
            }

        reasons = []

        # Check git commit
        current_commit = get_git_commit(self.project_root)
        if current_commit and current_commit != current_manifest.get("git_commit"):
            reasons.append(
                f"Git commit changed: {current_manifest.get('git_commit', 'unknown')[:8]} "
                f"-> {current_commit[:8]}"
            )

        # Check raw file hashes
        current_hashes = _get_raw_file_hashes(self.project_root)
        saved_hashes = current_manifest.get("raw_file_hashes", {})
        for fname, h in current_hashes.items():
            if fname not in saved_hashes:
                reasons.append(f"New raw file: {fname}")
            elif saved_hashes[fname] != h:
                reasons.append(f"Raw file changed: {fname}")
        for fname in saved_hashes:
            if fname not in current_hashes:
                reasons.append(f"Raw file removed: {fname}")

        # Check software versions
        current_sw = get_software_versions()
        saved_sw = current_manifest.get("software_versions", {})
        for pkg in ["pandas", "numpy", "geopandas"]:
            if current_sw.get(pkg) != saved_sw.get(pkg):
                reasons.append(
                    f"Package version changed: {pkg} "
                    f"{saved_sw.get(pkg, '?')} -> {current_sw.get(pkg, '?')}"
                )

        return {
            "needs_regeneration": len(reasons) > 0,
            "reasons": reasons,
        }

    def show_version(self) -> str:
        """Pretty-print version info for CLI."""
        m = self.load_manifest()
        if m is None:
            return "No data manifest found. Run the pipeline first."
        lines = [
            "EMS Data Version Info",
            "=" * 40,
            f"Generated at:  {m.get('generated_at', 'unknown')}",
            f"Git commit:    {m.get('git_commit', 'unknown')}",
            f"Git dirty:     {m.get('git_dirty', 'unknown')}",
            f"Seed:          {m.get('seed', 'unknown')}",
            "",
            "Software versions:",
        ]
        for pkg, ver in m.get("software_versions", {}).items():
            lines.append(f"  {pkg:15s}  {ver}")
        lines.append("")
        lines.append("Raw file hashes:")
        for fname, h in m.get("raw_file_hashes", {}).items():
            lines.append(f"  {fname:50s}  {h[:12]}...")
        return "\n".join(lines)
