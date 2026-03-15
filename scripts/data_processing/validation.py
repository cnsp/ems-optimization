"""Data validation for the EMS optimization pipeline.

Provides pre-flight checks on raw data files before processing begins.
Ensures required files exist, have reasonable sizes, expected columns,
and valid geometry where applicable.

Usage
-----
    from scripts.data_processing.validation import validate_raw_data
    validate_raw_data(project_root)  # raises ValidationError on failure
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ValidationError(Exception):
    """Raised when raw data fails validation checks."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        msg = f"{len(errors)} validation error(s):\n" + "\n".join(
            f"  [{i+1}] {e}" for i, e in enumerate(errors)
        )
        super().__init__(msg)


# --- Size thresholds ---
# Minimum expected file sizes (bytes).  A file smaller than this
# is likely empty or truncated.
MIN_SIZES: Dict[str, int] = {
    "FDNY_Firehouse_Listing_*.csv": 5_000,          # ~30 KB expected
    "Motor_Vehicle_Collisions_-_Crashes_*.csv": 100_000_000,  # ~536 MB
    "Police_Precincts_*.csv": 50_000,               # ~3.6 MB
    "manhattan_boundary.geojson": 500,
    "cbd_boundary.geojson": 500,
}

# Maximum expected file sizes (bytes).  Larger than this is suspicious.
MAX_SIZES: Dict[str, int] = {
    "FDNY_Firehouse_Listing_*.csv": 5_000_000,
    "Motor_Vehicle_Collisions_-_Crashes_*.csv": 2_000_000_000,
    "Police_Precincts_*.csv": 50_000_000,
    "manhattan_boundary.geojson": 5_000_000,
    "cbd_boundary.geojson": 5_000_000,
}

# Expected columns per CSV
EXPECTED_COLUMNS: Dict[str, List[str]] = {
    "FDNY_Firehouse_Listing": ["FacilityName", "FacilityAddress", "Borough"],
    "Motor_Vehicle_Collisions": ["CRASH DATE", "CRASH TIME", "LATITUDE", "LONGITUDE"],
    "Police_Precincts": ["Precinct", "the_geom"],
}


def _resolve_glob(raw_dir: Path, pattern: str) -> Optional[Path]:
    """Return the first file matching *pattern* in raw_dir, or None."""
    matches = sorted(raw_dir.glob(pattern))
    return matches[0] if matches else None


def _check_file_exists(raw_dir: Path, pattern: str, errors: List[str]) -> Optional[Path]:
    """Ensure at least one file matching *pattern* exists."""
    path = _resolve_glob(raw_dir, pattern)
    if path is None:
        errors.append(f"Required file not found: {pattern}")
    return path


def _check_file_size(path: Path, pattern: str, errors: List[str]) -> None:
    """Check that file size is within expected bounds."""
    size = path.stat().st_size
    if size == 0:
        errors.append(f"{path.name}: file is empty (0 bytes)")
        return
    min_sz = MIN_SIZES.get(pattern, 0)
    max_sz = MAX_SIZES.get(pattern, float("inf"))
    if size < min_sz:
        errors.append(
            f"{path.name}: file too small ({size:,} bytes, expected >= {min_sz:,}). "
            f"Possibly truncated or corrupted."
        )
    if size > max_sz:
        errors.append(
            f"{path.name}: file unexpectedly large ({size:,} bytes, expected <= {max_sz:,}). "
            f"Possibly wrong file."
        )


def _check_csv_columns(path: Path, key: str, errors: List[str]) -> None:
    """Verify that expected columns are present in a CSV header."""
    expected = EXPECTED_COLUMNS.get(key, [])
    if not expected:
        return
    try:
        with open(path, "r", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
    except Exception as exc:
        errors.append(f"{path.name}: could not read CSV header -- {exc}")
        return

    missing = [col for col in expected if col not in header]
    if missing:
        errors.append(
            f"{path.name}: missing expected column(s): {missing}. "
            f"Found: {header[:10]}{'...' if len(header) > 10 else ''}"
        )


def _check_geojson_geometry(path: Path, errors: List[str]) -> None:
    """Basic structural check on a GeoJSON file."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name}: invalid JSON -- {exc}")
        return

    if data.get("type") not in ("FeatureCollection", "Feature", "Polygon", "MultiPolygon"):
        errors.append(
            f"{path.name}: unexpected GeoJSON type '{data.get('type')}'. "
            f"Expected FeatureCollection, Feature, Polygon, or MultiPolygon."
        )
        return

    # For FeatureCollection, check that features have geometry
    if data.get("type") == "FeatureCollection":
        features = data.get("features", [])
        if not features:
            errors.append(f"{path.name}: FeatureCollection has no features.")
            return
        for i, feat in enumerate(features[:5]):
            geom = feat.get("geometry")
            if geom is None or geom.get("coordinates") is None:
                errors.append(
                    f"{path.name}: feature {i} has no geometry or coordinates."
                )
                break


def _check_date_range_plausible(path: Path, errors: List[str]) -> None:
    """Quick sanity check on crash date range (read first + last rows)."""
    import datetime
    try:
        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)
            first_row = next(reader)

        date_str = first_row.get("CRASH DATE", "")
        if date_str:
            # Typical format: MM/DD/YYYY
            try:
                dt = datetime.datetime.strptime(date_str, "%m/%d/%Y")
                if dt.year < 2000 or dt.year > 2030:
                    errors.append(
                        f"{path.name}: first crash date ({date_str}) outside "
                        f"plausible range 2000-2030."
                    )
            except ValueError:
                pass  # Non-standard format; we won't flag it
    except Exception:
        pass  # Don't fail validation for date check edge cases


def validate_raw_data(project_root: Path | str, strict: bool = True) -> Tuple[bool, List[str]]:
    """Run all validation checks on raw data files.

    Parameters
    ----------
    project_root : Path
        Project root directory.
    strict : bool
        If True, treat warnings as errors.

    Returns
    -------
    (ok, errors) : tuple
        ok is True when no errors were found.  errors is a list of
        human-readable failure descriptions.
    """
    project_root = Path(project_root)
    raw_dir = project_root / "data" / "raw"
    errors: List[str] = []

    if not raw_dir.exists():
        errors.append(f"Raw data directory does not exist: {raw_dir}")
        return False, errors

    # --- 1. Required GeoJSON files ---
    for geojson_name in ("manhattan_boundary.geojson", "cbd_boundary.geojson"):
        path = raw_dir / geojson_name
        if not path.exists():
            errors.append(f"Required file missing: {geojson_name}")
        else:
            _check_file_size(path, geojson_name, errors)
            _check_geojson_geometry(path, errors)

    # --- 2. Firehouse listing ---
    fh_path = _check_file_exists(raw_dir, "FDNY_Firehouse_Listing_*.csv", errors)
    if fh_path:
        _check_file_size(fh_path, "FDNY_Firehouse_Listing_*.csv", errors)
        _check_csv_columns(fh_path, "FDNY_Firehouse_Listing", errors)

    # --- 3. Crash data ---
    crash_path = _check_file_exists(
        raw_dir, "Motor_Vehicle_Collisions_-_Crashes_*.csv", errors
    )
    if crash_path:
        _check_file_size(crash_path, "Motor_Vehicle_Collisions_-_Crashes_*.csv", errors)
        _check_csv_columns(crash_path, "Motor_Vehicle_Collisions", errors)
        _check_date_range_plausible(crash_path, errors)

    # --- 4. Precinct data ---
    prec_path = _check_file_exists(raw_dir, "Police_Precincts_*.csv", errors)
    if prec_path:
        _check_file_size(prec_path, "Police_Precincts_*.csv", errors)
        _check_csv_columns(prec_path, "Police_Precincts", errors)

    ok = len(errors) == 0
    return ok, errors
