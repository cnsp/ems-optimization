"""Main SimPy discrete-event simulation engine for EMS operations.

Orchestrates the full simulation loop:
    1. Generate NHPP incident arrivals
    2. Dispatch nearest available unit (or queue if none available)
    3. Model travel + on-scene service
    4. Collect performance metrics

Usage
-----
>>> from ems_readiness.simulation.engine import EMSSimulation
>>> sim = EMSSimulation(policy_allocation=alloc, seed=42)
>>> sim.run(horizon_hours=168)
>>> results = sim.get_results()
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import simpy
import yaml

from ems_readiness.demand.arrival_generator import NHPPArrivalGenerator
from ems_readiness.service.service_time import ServiceTimeModel
from ems_readiness.simulation.dispatcher import NearestAvailableDispatcher
from ems_readiness.simulation.entities import Incident
from ems_readiness.simulation.metrics import MetricsCollector
from ems_readiness.simulation.resources import EMSUnit, UnitPool

logger = logging.getLogger(__name__)


class EMSSimulation:
    """SimPy-based discrete-event simulation of EMS operations.

    Parameters
    ----------
    policy_allocation : pd.Series
        Firehouse name → number of units allocated.
    config : dict or None
        Simulation configuration (loaded from simulation.yaml if None).
    seed : int or None
        Random seed for reproducibility.
    data_dir : str or Path
        Path to processed data directory.
    project_root : str or Path
        Path to project root for loading configs.
    trace : bool
        Enable trace logging of individual events.
    """

    def __init__(
        self,
        policy_allocation: pd.Series,
        config: Optional[Dict] = None,
        seed: Optional[int] = 42,
        data_dir: str | Path = "data/processed",
        project_root: str | Path = ".",
        trace: bool = False,
    ):
        # Validate inputs
        if policy_allocation is None or policy_allocation.sum() <= 0:
            raise ValueError("policy_allocation must have at least one unit.")

        self.project_root = Path(project_root)
        self.data_dir = Path(data_dir)
        self.seed = seed
        self.trace = trace

        # Load configuration
        if config is None:
            config = self._load_config()
        self.config = config

        # Override trace from config if not explicitly set
        if not trace and config.get("trace_mode", False):
            self.trace = True

        # Core parameters
        self.response_threshold = config.get("response_threshold_minutes", 8.0)
        self.dispatch_delay_fixed = self._load_dispatch_delay()

        # Random number generator
        self._rng = np.random.default_rng(seed)

        # SimPy environment
        self.env = simpy.Environment()

        # Unit pool
        self.unit_pool = UnitPool(policy_allocation)
        logger.info(
            f"Initialized UnitPool: {self.unit_pool.total_units} units "
            f"across {len([f for f, n in policy_allocation.items() if n > 0])} firehouses"
        )

        # Arrival generator
        self.arrival_gen = self._init_arrival_generator()

        # Service time model
        self.service_model = self._init_service_model()

        # Dispatcher
        self.dispatcher = self._init_dispatcher()

        # Metrics collector
        additional_thresholds = tuple(config.get("additional_thresholds", [6.0]))
        self.metrics = MetricsCollector(
            response_threshold_minutes=self.response_threshold,
            additional_thresholds=additional_thresholds,
        )

        # Internal state – FIFO queue of (incident, simpy.Event) pairs
        self._waiting_queue: list[tuple[Incident, simpy.Event]] = []
        self._incident_counter = 0
        self._completed = False

    # ── Configuration Loading ────────────────────────────────────────

    def _load_config(self) -> Dict:
        """Load simulation configuration from YAML."""
        config_path = self.project_root / "configs" / "simulation.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        logger.warning(
            f"Config not found at {config_path}; using defaults."
        )
        return {
            "horizon_hours": 168,
            "warmup_hours": 0,
            "num_replications": 30,
            "seed_base": 42,
            "response_threshold_minutes": 8.0,
            "additional_thresholds": [6.0],
            "trace_mode": False,
        }

    def _load_dispatch_delay(self) -> float:
        """Load fixed dispatch delay from service config."""
        svc_path = self.project_root / "configs" / "service.yaml"
        if svc_path.exists():
            with open(svc_path) as f:
                svc = yaml.safe_load(f)
            return svc.get("dispatch_delay_minutes", 1.5)
        return 1.5

    def _init_arrival_generator(self) -> NHPPArrivalGenerator:
        """Initialize the NHPP arrival generator from data tables."""
        data_path = self.project_root / self.data_dir
        if (data_path / "demand_lambda_hourly.csv").exists():
            return NHPPArrivalGenerator.from_tables(
                data_dir=str(data_path)
            )
        logger.warning("Lambda tables not found; using default generator.")
        return NHPPArrivalGenerator()

    def _init_service_model(self) -> ServiceTimeModel:
        """Initialize the service time model from config."""
        svc_path = self.project_root / "configs" / "service.yaml"
        if svc_path.exists():
            with open(svc_path) as f:
                svc = yaml.safe_load(f)
            st = svc.get("service_time", {})
            return ServiceTimeModel(
                mean_minutes=st.get("mean_minutes", 25.0),
                std_minutes=st.get("std_minutes", 10.0),
                distribution=st.get("distribution", "lognormal"),
            )
        return ServiceTimeModel()

    def _init_dispatcher(self) -> NearestAvailableDispatcher:
        """Initialize the dispatcher with distance matrix."""
        dm_path = self.project_root / self.data_dir / "distance_matrix_firehouse_precinct.csv"
        if dm_path.exists():
            dm = pd.read_csv(dm_path, index_col=0)
            # Ensure column names are strings
            dm.columns = dm.columns.astype(str)
        else:
            raise FileNotFoundError(
                f"Distance matrix not found at {dm_path}. "
                "Run data processing first."
            )

        svc_path = self.project_root / "configs" / "service.yaml"
        speed = 20.0
        use_tod = True
        if svc_path.exists():
            with open(svc_path) as f:
                svc = yaml.safe_load(f)
            tt = svc.get("travel_time", {})
            speed = tt.get("average_speed_mph", 20.0)
            use_tod = tt.get("use_time_of_day", True)

        return NearestAvailableDispatcher(
            distance_matrix=dm,
            speed_mph=speed,
            use_time_of_day=use_tod,
        )

    # ── SimPy Processes ──────────────────────────────────────────────

    def _arrival_process(self, horizon_hours: float):
        """SimPy generator: produce incidents over the horizon.

        Uses the NHPP arrival generator to create batches of arrivals
        per simulated day, then yields them at the correct simulation time.
        """
        hours_per_day = 24.0
        n_days = int(np.ceil(horizon_hours / hours_per_day))
        current_time = 0.0

        for day in range(n_days):
            dow = day % 7  # 0=Mon, cycle through week
            remaining = min(hours_per_day, horizon_hours - current_time)
            if remaining <= 0:
                break

            # Generate arrivals for this day
            day_seed = self._rng.integers(0, 2**31)
            arrivals_df = self.arrival_gen.generate_arrivals(
                n_hours=remaining,
                start_hour=0,
                dow=dow,
                rng=int(day_seed),
            )

            for _, row in arrivals_df.iterrows():
                t_arrival = current_time + row["time_hours"]
                if t_arrival >= horizon_hours:
                    break

                # Wait until this arrival time
                wait = t_arrival - self.env.now
                if wait > 0:
                    yield self.env.timeout(wait)

                # Create incident
                self._incident_counter += 1
                precinct = int(row.get("precinct", 1))
                incident = Incident(
                    id=self._incident_counter,
                    arrival_time=self.env.now,
                    precinct=precinct,
                )

                if self.trace:
                    logger.info(
                        f"[t={self.env.now:.3f}h] Incident #{incident.id} "
                        f"arrived at precinct {precinct}"
                    )

                # Start incident handling as a separate process
                self.env.process(self._incident_handler(incident))

            current_time += remaining

    def _signal_waiting_queue(self):
        """Wake up the first waiting incident in the FIFO queue, if any."""
        if self._waiting_queue:
            _, evt = self._waiting_queue[0]
            if not evt.triggered:
                evt.succeed()

    def _incident_handler(self, incident: Incident):
        """SimPy generator: handle a single incident.

        Steps:
            1. Fixed dispatch delay
            2. Find nearest available unit (or wait in FIFO queue)
            3. Travel to scene
            4. On-scene service
            5. Return unit to available pool & signal queue
        """
        # Record queue length at arrival
        queue_len = len(self._waiting_queue)
        self.metrics.record_queue_length(self.env.now, queue_len)

        # Step 1: Fixed dispatch delay
        dispatch_delay_hours = self.dispatch_delay_fixed / 60.0
        yield self.env.timeout(dispatch_delay_hours)

        # Step 2: Find nearest available unit
        hour_of_day = int(incident.arrival_time) % 24  # approximate hour
        unit, travel_time_min = self.dispatcher.find_nearest_unit(
            precinct=incident.precinct,
            unit_pool=self.unit_pool,
            hour_of_day=hour_of_day,
        )

        # If no unit available, enter FIFO queue and wait
        queue_wait_start = self.env.now
        if unit is None:
            incident.queued = True
            wait_event = self.env.event()
            self._waiting_queue.append((incident, wait_event))
            queue_len = len(self._waiting_queue)
            self.metrics.record_queue_length(self.env.now, queue_len)

            if self.trace:
                logger.info(
                    f"[t={self.env.now:.3f}h] Incident #{incident.id} "
                    f"queued (queue_len={queue_len})"
                )

            # Wait until signalled that a unit is free AND we're first in queue
            while unit is None:
                yield wait_event
                # Re-check availability (we should be first in queue now)
                unit, travel_time_min = self.dispatcher.find_nearest_unit(
                    precinct=incident.precinct,
                    unit_pool=self.unit_pool,
                    hour_of_day=int(self.env.now) % 24,
                )
                if unit is not None:
                    # Remove ourselves from queue
                    self._waiting_queue = [
                        (inc, ev) for inc, ev in self._waiting_queue
                        if inc.id != incident.id
                    ]
                    queue_len = len(self._waiting_queue)
                    self.metrics.record_queue_length(self.env.now, queue_len)
                else:
                    # Unit was taken by concurrent process; re-create event
                    wait_event = self.env.event()
                    # Update our event in the queue
                    self._waiting_queue = [
                        (inc, wait_event if inc.id == incident.id else ev)
                        for inc, ev in self._waiting_queue
                    ]

        queue_wait_hours = self.env.now - queue_wait_start

        # Dispatch the unit
        incident.dispatch_time = self.env.now
        incident.assigned_unit = unit.id
        incident.assigned_firehouse = unit.home_firehouse
        incident.dispatch_delay_minutes = (
            self.dispatch_delay_fixed + queue_wait_hours * 60.0
        )
        unit.dispatch()

        if self.trace:
            logger.info(
                f"[t={self.env.now:.3f}h] Incident #{incident.id} → "
                f"unit {unit.id} (travel={travel_time_min:.1f} min)"
            )

        # Step 3: Travel to scene
        incident.travel_time_minutes = travel_time_min
        travel_hours = travel_time_min / 60.0
        yield self.env.timeout(travel_hours)

        # Step 4: On-scene service
        incident.service_start_time = self.env.now
        unit.arrive_on_scene()

        service_time = self.service_model.sample(size=1, rng=self._rng)[0]
        incident.service_time_minutes = service_time
        service_hours = service_time / 60.0
        yield self.env.timeout(service_hours)

        # Step 5: Complete – return unit to available pool
        incident.completion_time = self.env.now
        busy_duration = travel_hours + service_hours
        unit.return_available(busy_duration)

        # Record metrics
        self.metrics.record_incident(incident)

        if self.trace:
            logger.info(
                f"[t={self.env.now:.3f}h] Incident #{incident.id} completed. "
                f"Response={incident.response_time_minutes:.1f} min"
            )

        # Signal the first waiting incident in the queue
        self._signal_waiting_queue()

    # ── Public Interface ─────────────────────────────────────────────

    def run(self, horizon_hours: Optional[float] = None) -> None:
        """Execute the simulation.

        Parameters
        ----------
        horizon_hours : float or None
            Duration to simulate (hours). Uses config default if None.
        """
        if horizon_hours is None:
            horizon_hours = self.config.get("horizon_hours", 168)

        logger.info(
            f"Starting simulation: horizon={horizon_hours}h, "
            f"units={self.unit_pool.total_units}, seed={self.seed}"
        )

        # Register the arrival process
        self.env.process(self._arrival_process(horizon_hours))

        # Run
        self.env.run(until=horizon_hours)
        self._completed = True

        logger.info(
            f"Simulation complete: {self.metrics._total_incidents} incidents, "
            f"coverage={self.metrics.get_summary_statistics().get('coverage_fraction', 0):.1%}"
        )

    def get_results(self) -> Dict[str, Any]:
        """Return simulation results.

        Returns
        -------
        dict
            Keys: 'summary', 'incident_log', 'unit_utilizations',
                  'firehouse_utilizations', 'config'.
        """
        horizon = self.config.get("horizon_hours", 168)
        summary = self.metrics.get_summary_statistics()
        summary["total_units"] = self.unit_pool.total_units
        summary["horizon_hours"] = horizon

        return {
            "summary": summary,
            "incident_log": self.metrics.get_incident_log(),
            "unit_utilizations": self.unit_pool.get_utilizations(horizon),
            "firehouse_utilizations": self.unit_pool.get_firehouse_utilizations(horizon),
            "config": self.config,
        }

    def __repr__(self) -> str:
        status = "completed" if self._completed else "ready"
        return (
            f"EMSSimulation(units={self.unit_pool.total_units}, "
            f"seed={self.seed}, status={status})"
        )
