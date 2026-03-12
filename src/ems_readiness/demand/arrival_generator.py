"""Non-Homogeneous Poisson Process (NHPP) arrival generator.

Generates EMS call arrival times using thinning (Lewis-Shedler) algorithm
applied to pre-computed lambda tables from the demand model.

Inputs
------
* ``demand_lambda_hourly.csv`` – hourly intensity factors.
* ``demand_lambda_dow.csv``    – day-of-week factors.
* ``demand_lambda_precinct.csv`` – per-precinct base rates.

Algorithm
---------
For each (day, hour) interval the effective rate is:
    λ(t) = base_rate × hourly_factor(hour) × dow_factor(day_of_week)

We use the *thinning* algorithm (Lewis & Shedler 1979) with the
maximum rate as the envelope.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


# ── Helpers ──────────────────────────────────────────────────────────

def load_lambda_tables(
    data_dir: str | Path = "data/processed",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load pre-computed demand lambda tables.

    Returns
    -------
    hourly : pd.DataFrame  – columns: hour, lambda_per_hour, factor, …
    dow    : pd.DataFrame  – columns: dow, day_name, factor, …
    precinct : pd.DataFrame – columns: precinct, lambda_per_hour, …
    """
    data_dir = Path(data_dir)
    hourly = pd.read_csv(data_dir / "demand_lambda_hourly.csv")
    dow = pd.read_csv(data_dir / "demand_lambda_dow.csv")
    precinct = pd.read_csv(data_dir / "demand_lambda_precinct.csv")
    return hourly, dow, precinct


def effective_rate(
    base_rate: float,
    hour: int,
    dow: int,
    hourly_factors: dict[int, float],
    dow_factors: dict[int, float],
) -> float:
    """Compute λ(t) = base_rate × hourly_factor × dow_factor."""
    return base_rate * hourly_factors.get(hour, 1.0) * dow_factors.get(dow, 1.0)


# ── Main generator ───────────────────────────────────────────────────

class NHPPArrivalGenerator:
    """Generate arrival times via a Non-Homogeneous Poisson Process.

    Parameters
    ----------
    base_rate : float
        Overall base arrival rate (calls / hour).
    hourly_factors : dict[int, float]
        Hour (0–23) → multiplicative factor.
    dow_factors : dict[int, float]
        Day-of-week (0=Mon … 6=Sun) → multiplicative factor.
    precinct_rates : dict | None
        Precinct → calls/hour.  Used for spatial allocation.
    """

    def __init__(
        self,
        base_rate: float = 3.48,
        hourly_factors: dict[int, float] | None = None,
        dow_factors: dict[int, float] | None = None,
        precinct_rates: dict[int, float] | None = None,
    ):
        self.base_rate = base_rate
        self.hourly_factors = hourly_factors or {h: 1.0 for h in range(24)}
        self.dow_factors = dow_factors or {d: 1.0 for d in range(7)}
        self.precinct_rates = precinct_rates

        # Pre-compute precinct probabilities for spatial allocation
        if precinct_rates is not None:
            total = sum(precinct_rates.values())
            self._precinct_ids = list(precinct_rates.keys())
            self._precinct_probs = np.array(
                [precinct_rates[p] / total for p in self._precinct_ids]
            )
        else:
            self._precinct_ids = None
            self._precinct_probs = None

    # ── Factory ──────────────────────────────────────────────────────
    @classmethod
    def from_tables(
        cls, data_dir: str | Path = "data/processed", base_rate: float = 3.48
    ) -> "NHPPArrivalGenerator":
        """Construct from saved CSV lambda tables."""
        hourly, dow, precinct = load_lambda_tables(data_dir)
        hourly_factors = dict(zip(hourly["hour"].astype(int), hourly["factor"]))
        dow_factors = dict(zip(dow["dow"].astype(int), dow["factor"]))
        precinct_rates = dict(
            zip(precinct["precinct"].astype(int), precinct["lambda_per_hour"])
        )
        return cls(
            base_rate=base_rate,
            hourly_factors=hourly_factors,
            dow_factors=dow_factors,
            precinct_rates=precinct_rates,
        )

    # ── Thinning algorithm ───────────────────────────────────────────
    def generate_arrivals(
        self,
        n_hours: float = 24.0,
        start_hour: int = 0,
        dow: int = 0,
        rng: int | np.random.Generator | None = None,
    ) -> pd.DataFrame:
        """Generate arrival times for a given time window.

        Parameters
        ----------
        n_hours : float
            Duration of the simulation window (hours).
        start_hour : int
            Clock hour at the start of the window (0–23).
        dow : int
            Day-of-week index (0=Monday … 6=Sunday).
        rng : int, Generator, or None
            Random seed or Generator.

        Returns
        -------
        pd.DataFrame
            Columns: ``time_hours``, ``hour``, ``precinct`` (if spatial
            allocation is enabled).
        """
        if isinstance(rng, (int, np.integer)):
            rng = np.random.default_rng(rng)
        elif rng is None:
            rng = np.random.default_rng()

        # Compute maximum λ across the window for the thinning envelope
        rates = [
            effective_rate(
                self.base_rate,
                (start_hour + int(h)) % 24,
                dow,
                self.hourly_factors,
                self.dow_factors,
            )
            for h in range(int(np.ceil(n_hours)))
        ]
        lambda_max = max(rates) * 1.05  # small buffer

        # Thinning (Lewis-Shedler)
        arrivals: list[float] = []
        t = 0.0
        while t < n_hours:
            # Inter-arrival from homogeneous Poisson with rate lambda_max
            t += rng.exponential(1.0 / lambda_max)
            if t >= n_hours:
                break
            current_hour = (start_hour + int(t)) % 24
            lam_t = effective_rate(
                self.base_rate, current_hour, dow,
                self.hourly_factors, self.dow_factors,
            )
            # Accept with probability λ(t) / λ_max
            if rng.uniform() < lam_t / lambda_max:
                arrivals.append(t)

        df = pd.DataFrame({"time_hours": arrivals})
        df["hour"] = ((start_hour + df["time_hours"]).astype(int)) % 24

        # Spatial allocation
        if self._precinct_ids is not None and len(df) > 0:
            df["precinct"] = rng.choice(
                self._precinct_ids, size=len(df), p=self._precinct_probs
            )

        return df

    def __repr__(self) -> str:
        return (
            f"NHPPArrivalGenerator(base_rate={self.base_rate:.2f}, "
            f"n_precincts={len(self._precinct_ids) if self._precinct_ids else 0})"
        )
