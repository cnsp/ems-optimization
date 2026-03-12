"""Discrete-event simulation engine for EMS readiness optimization.

Provides a SimPy-based simulation of EMS operations including:
- NHPP incident arrivals
- Nearest-available unit dispatch
- Travel time and service time modeling
- Performance metrics collection
- Batch execution with multiple replications

Key classes:
    EMSSimulation   – main simulation engine
    BatchRunner     – multi-replication runner
    MetricsCollector – statistics collection
"""

from ems_readiness.simulation.engine import EMSSimulation
from ems_readiness.simulation.runner import BatchRunner
from ems_readiness.simulation.metrics import MetricsCollector
from ems_readiness.simulation.entities import Incident
from ems_readiness.simulation.resources import EMSUnit, UnitPool
from ems_readiness.simulation.dispatcher import NearestAvailableDispatcher

__all__ = [
    "EMSSimulation",
    "BatchRunner",
    "MetricsCollector",
    "Incident",
    "EMSUnit",
    "UnitPool",
    "NearestAvailableDispatcher",
]
