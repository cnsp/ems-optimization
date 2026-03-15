"""Reproducibility and seed management for EMS simulations.

Provides a centralized SeedManager that derives deterministic,
independent seeds for each stochastic component from a single
master seed.  This guarantees:

    1. Full reproducibility: same master seed => identical results.
    2. Component isolation: changing one component's code path does
       not alter another component's random stream.
    3. Auditability: all seeds are logged and can be stored in
       output metadata for exact reproduction.

Usage
-----
>>> from ems_readiness.utils.reproducibility import SeedManager
>>> sm = SeedManager(master_seed=42)
>>> sm.set_global_seeds()          # sets numpy/random module seeds
>>> rng = sm.get_rng("simulation") # independent Generator for simulation
>>> sm.log_seeds()                 # returns dict for metadata logging

Configuration
-------------
Seeds can be loaded from ``configs/reproducibility.yaml`` via
``SeedManager.from_config(project_root)``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import yaml

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────

DEFAULT_MASTER_SEED: int = 42

# Component names recognized by the seed hierarchy.
COMPONENT_NAMES: List[str] = [
    "demand",
    "simulation",
    "service",
    "optimization",
    "analysis",
]


# ── SeedManager ───────────────────────────────────────────────────


class SeedManager:
    """Centralized seed management for reproducible experiments.

    Parameters
    ----------
    master_seed : int or None
        Master seed from which all component seeds are derived.
        If *None*, uses ``DEFAULT_MASTER_SEED`` (42).
    component_overrides : dict or None
        Explicit per-component seeds that override the derived values.
        Example: ``{"demand": 99, "simulation": 100}``.
    log_seeds : bool
        If *True*, emit an INFO log line with all seeds on creation.
    """

    def __init__(
        self,
        master_seed: Optional[int] = None,
        component_overrides: Optional[Dict[str, int]] = None,
        log_seeds: bool = True,
    ):
        self.master_seed: int = master_seed if master_seed is not None else DEFAULT_MASTER_SEED
        self._overrides: Dict[str, int] = component_overrides or {}
        self._seeds: Dict[str, int] = self._derive_seeds()
        self._rngs: Dict[str, np.random.Generator] = {}

        if log_seeds:
            logger.info(f"SeedManager initialised: {self.summary()}")

    # ── Seed derivation ───────────────────────────────────────────

    def _derive_seeds(self) -> Dict[str, int]:
        """Derive deterministic component seeds from the master seed.

        Uses a keyed hash so that each component gets a unique,
        reproducible seed regardless of enumeration order.
        """
        seeds: Dict[str, int] = {}
        for name in COMPONENT_NAMES:
            if name in self._overrides:
                seeds[name] = self._overrides[name]
            else:
                # Hash master_seed + component name for deterministic derivation
                key = f"{self.master_seed}:{name}"
                h = hashlib.sha256(key.encode()).hexdigest()
                seeds[name] = int(h[:8], 16)  # 32-bit derived seed
        return seeds

    # ── Public API ────────────────────────────────────────────────

    def get_seed(self, component: str) -> int:
        """Return the seed for *component*.

        Parameters
        ----------
        component : str
            One of ``COMPONENT_NAMES`` or any string previously
            registered via ``_derive_seeds``.

        Returns
        -------
        int
        """
        if component not in self._seeds:
            # Derive on the fly for unknown components
            key = f"{self.master_seed}:{component}"
            h = hashlib.sha256(key.encode()).hexdigest()
            self._seeds[component] = int(h[:8], 16)
        return self._seeds[component]

    def get_rng(self, component: str) -> np.random.Generator:
        """Return an independent ``numpy.random.Generator`` for *component*.

        The generator is created lazily and cached so that multiple calls
        for the same component return the **same** generator instance (and
        therefore the same random stream).
        """
        if component not in self._rngs:
            self._rngs[component] = np.random.default_rng(self.get_seed(component))
        return self._rngs[component]

    def set_global_seeds(self) -> None:
        """Set ``random`` and ``numpy.random`` module-level seeds.

        Useful as a belt-and-suspenders measure for third-party code that
        uses the legacy global PRNG.
        """
        random.seed(self.master_seed)
        np.random.seed(self.master_seed)
        logger.debug(f"Global seeds set to master_seed={self.master_seed}")

    def summary(self) -> Dict[str, Any]:
        """Return a JSON-serialisable summary of all seeds."""
        return {
            "master_seed": self.master_seed,
            "component_seeds": dict(self._seeds),
            "overrides_applied": list(self._overrides.keys()) if self._overrides else [],
        }

    def log_seeds(self) -> Dict[str, Any]:
        """Log and return the full seed summary (alias for ``summary``)."""
        info = self.summary()
        logger.info(f"Seed summary: {json.dumps(info)}")
        return info

    def to_metadata(self) -> Dict[str, Any]:
        """Return metadata dict suitable for embedding in output files."""
        return {
            "reproducibility": {
                "master_seed": self.master_seed,
                "component_seeds": dict(self._seeds),
            }
        }

    # ── Factory methods ───────────────────────────────────────────

    @classmethod
    def from_config(cls, project_root: str | Path = ".") -> "SeedManager":
        """Create a ``SeedManager`` from ``configs/reproducibility.yaml``.

        Falls back to defaults if the file does not exist.
        """
        cfg_path = Path(project_root) / "configs" / "reproducibility.yaml"
        if cfg_path.exists():
            with open(cfg_path) as f:
                cfg = yaml.safe_load(f) or {}
            repro = cfg.get("reproducibility", {})
            master = repro.get("master_seed", DEFAULT_MASTER_SEED)
            overrides = repro.get("component_seeds", None)
            log_flag = repro.get("log_seeds", True)
            return cls(
                master_seed=master,
                component_overrides=overrides,
                log_seeds=log_flag,
            )
        logger.warning(
            f"Config not found at {cfg_path}; using defaults (master_seed={DEFAULT_MASTER_SEED})"
        )
        return cls()

    # ── Dunder ────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"SeedManager(master_seed={self.master_seed}, "
            f"components={list(self._seeds.keys())})"
        )
