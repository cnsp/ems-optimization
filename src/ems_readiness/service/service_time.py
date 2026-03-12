"""On-scene service-time distribution for EMS calls.

Model Choice
------------
We use a **LogNormal** distribution for total service time (dispatch +
travel-to-scene + on-scene care + return-to-available).  LogNormal is
standard in EMS operations research because:

1. Service times are strictly positive.
2. The distribution is right-skewed (most calls resolved quickly, some
   take much longer).
3. Empirical EMS data consistently fits LogNormal better than Exponential
   (see Goldberg 2004; Ingolfsson et al. 2008).

Default Parameters
------------------
* **Mean service time**: 25 minutes (covers on-scene care; travel time
  is handled separately by the travel-time module).
* **Std deviation**: 10 minutes.
* These translate to LogNormal μ and σ via moment-matching.

Usage
-----
>>> from ems_readiness.service.service_time import ServiceTimeModel
>>> model = ServiceTimeModel(mean_minutes=25, std_minutes=10)
>>> samples = model.sample(100, rng=42)
"""

from __future__ import annotations

import numpy as np


def _lognormal_params(mean: float, std: float) -> tuple[float, float]:
    """Convert desired (mean, std) to LogNormal (mu, sigma) parameters.

    Uses standard moment-matching formulas:
        sigma² = ln(1 + (std/mean)²)
        mu     = ln(mean) - sigma²/2
    """
    variance = std ** 2
    sigma2 = np.log(1.0 + variance / mean ** 2)
    mu = np.log(mean) - sigma2 / 2.0
    return mu, np.sqrt(sigma2)


class ServiceTimeModel:
    """Callable model that samples from a service-time distribution.

    Parameters
    ----------
    mean_minutes : float
        Desired mean of the service-time distribution.
    std_minutes : float
        Desired standard deviation.
    distribution : str
        One of ``'lognormal'`` or ``'exponential'``.
    """

    SUPPORTED_DISTRIBUTIONS = ("lognormal", "exponential")

    def __init__(
        self,
        mean_minutes: float = 25.0,
        std_minutes: float = 10.0,
        distribution: str = "lognormal",
    ):
        distribution = distribution.lower()
        if distribution not in self.SUPPORTED_DISTRIBUTIONS:
            raise ValueError(
                f"Unsupported distribution '{distribution}'. "
                f"Choose from {self.SUPPORTED_DISTRIBUTIONS}."
            )
        self.mean_minutes = mean_minutes
        self.std_minutes = std_minutes
        self.distribution = distribution

        if distribution == "lognormal":
            self._mu, self._sigma = _lognormal_params(mean_minutes, std_minutes)

    # ── Sampling ─────────────────────────────────────────────────────
    def sample(
        self,
        size: int = 1,
        rng: int | np.random.Generator | None = None,
    ) -> np.ndarray:
        """Draw *size* service-time samples (minutes).

        Parameters
        ----------
        size : int
            Number of samples.
        rng : int, Generator, or None
            Random seed or NumPy Generator for reproducibility.

        Returns
        -------
        np.ndarray of shape (size,)
        """
        if isinstance(rng, (int, np.integer)):
            rng = np.random.default_rng(rng)
        elif rng is None:
            rng = np.random.default_rng()

        if self.distribution == "lognormal":
            return rng.lognormal(mean=self._mu, sigma=self._sigma, size=size)
        else:  # exponential
            return rng.exponential(scale=self.mean_minutes, size=size)

    def __repr__(self) -> str:
        return (
            f"ServiceTimeModel(distribution='{self.distribution}', "
            f"mean={self.mean_minutes:.1f} min, std={self.std_minutes:.1f} min)"
        )
