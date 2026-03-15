#!/usr/bin/env python3
"""Generate all processed data from raw inputs.

This is the single entry-point for the data processing pipeline.
It can be run standalone or imported by notebooks to auto-generate
missing data.

Usage
-----
    # Full pipeline (regenerate everything):
    python scripts/generate_all_data.py --force

    # Normal run (skip files that already exist):
    python scripts/generate_all_data.py

    # Skip input validation:
    python scripts/generate_all_data.py --no-validate

    # Parallel processing (4 workers):
    python scripts/generate_all_data.py --jobs 4

    # Show current data version:
    python scripts/generate_all_data.py --version

    # Specific tier only:
    python scripts/generate_all_data.py --tier 3

    # Verify data exists without generating:
    python scripts/generate_all_data.py --verify
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def verify_raw_data(project_root: Path) -> bool:
    """Check that required raw files exist, print helpful messages."""
    raw = project_root / "data" / "raw"
    required = {
        "FDNY_Firehouse_Listing_*.csv": "Tracked in repo -- should always exist.",
        "manhattan_boundary.geojson": "Tracked in repo.",
        "cbd_boundary.geojson": "Tracked in repo.",
    }
    optional_large = {
        "Motor_Vehicle_Collisions_-_Crashes_*.csv": (
            "Download from: https://data.cityofnewyork.us/Public-Safety/"
            "Motor-Vehicle-Collisions-Crashes/h9gi-nx95"
        ),
        "Police_Precincts_*.csv": (
            "Download from: https://data.cityofnewyork.us/Public-Safety/"
            "Police-Precincts/kmub-pusk"
        ),
    }

    ok = True
    for pattern, msg in required.items():
        if not list(raw.glob(pattern)):
            print(f"  [MISSING] {pattern}  -- {msg}")
            ok = False
        else:
            print(f"  [OK]      {pattern}")

    for pattern, msg in optional_large.items():
        if not list(raw.glob(pattern)):
            print(f"  [MISSING] {pattern}")
            print(f"            {msg}")
            ok = False
        else:
            print(f"  [OK]      {pattern}")

    return ok


def verify_processed_data(project_root: Path) -> bool:
    """Check that all expected processed files exist."""
    processed = project_root / "data" / "processed"
    expected = [
        "firehouses_clean.csv",
        "firehouses_manhattan.csv",
        "precincts_manhattan.geojson",
        "crashes_manhattan.csv",
        "crashes_manhattan.parquet",
        "demand_lambda_hourly.csv",
        "demand_lambda_dow.csv",
        "demand_lambda_precinct.csv",
        "demand_model_summary.json",
        "distance_matrix_firehouse_precinct.csv",
        "distance_matrix_firehouse_precinct_manhattan.csv",
    ]
    all_ok = True
    for name in expected:
        path = processed / name
        if path.exists():
            size = path.stat().st_size
            print(f"  [OK]      {name}  ({size:,} bytes)")
        else:
            print(f"  [MISSING] {name}")
            all_ok = False
    return all_ok


def ensure_data(project_root: str | Path = None, force: bool = False) -> None:
    """Ensure all processed data exists, generating if needed.

    This is the function notebooks should call to auto-generate
    missing data before they start their analysis.

    Parameters
    ----------
    project_root : Path, optional
        Project root. Auto-detected if None.
    force : bool
        Regenerate all files.
    """
    if project_root is None:
        project_root = PROJECT_ROOT
    project_root = Path(project_root)

    from scripts.data_processing import run_full_pipeline

    if not force:
        # Quick check -- if everything exists, skip
        processed = project_root / "data" / "processed"
        key_files = [
            "firehouses_manhattan.csv",
            "crashes_manhattan.parquet",
            "demand_lambda_hourly.csv",
            "distance_matrix_firehouse_precinct.csv",
        ]
        if all((processed / f).exists() for f in key_files):
            return  # All key files present, nothing to do

    print("\n[Auto-generate] Some processed data files are missing.")
    print("[Auto-generate] Generating from raw inputs...\n")
    run_full_pipeline(project_root, force=force)


def main():
    parser = argparse.ArgumentParser(
        description="Generate all processed data for EMS Optimization project."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Regenerate all files even if they already exist.",
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Only verify data existence (no generation).",
    )
    parser.add_argument(
        "--tier", type=int, choices=[1, 2, 3],
        help="Run only a specific tier (1=boundaries, 2=spatial, 3=demand+distance).",
    )
    parser.add_argument(
        "--no-validate", action="store_true",
        help="Skip raw data validation checks before processing.",
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Disable smart caching (process even if inputs unchanged).",
    )
    parser.add_argument(
        "--jobs", "-j", type=int, default=1,
        help="Number of parallel workers (default: 1). Use 0 for auto-detect CPU count.",
    )
    parser.add_argument(
        "--version", action="store_true",
        help="Show current data version and exit.",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Master seed for reproducibility (default: 42).",
    )
    args = parser.parse_args()

    project_root = PROJECT_ROOT

    # --- Handle --version flag ---
    if args.version:
        from scripts.data_processing.versioning import DataVersionManager
        dvm = DataVersionManager(project_root)
        print(dvm.show_version())
        return

    # --- Resolve parallel workers ---
    n_jobs = args.jobs
    if n_jobs == 0:
        n_jobs = os.cpu_count() or 1
    if n_jobs < 0:
        n_jobs = max(1, (os.cpu_count() or 1) + n_jobs + 1)

    print("=" * 60)
    print("EMS OPTIMIZATION - DATA PIPELINE")
    print("=" * 60)

    # --- Data validation ---
    if not args.no_validate and not args.verify:
        print("\nValidating raw data...")
        from scripts.data_processing.validation import validate_raw_data, ValidationError
        ok, errors = validate_raw_data(project_root)
        if ok:
            print("  All validation checks passed.")
        else:
            print(f"\n  {len(errors)} validation issue(s) found:")
            for e in errors:
                print(f"    - {e}")
            if args.force:
                print("\n  Continuing anyway (--force specified)...")
            else:
                print("\n  Use --no-validate to skip, or --force to continue anyway.")
                # Don't exit -- the pipeline will skip missing data steps gracefully

    # Verify raw data
    print("\nChecking raw data...")
    raw_ok = verify_raw_data(project_root)
    if not raw_ok:
        print("\n[WARNING] Some raw files are missing.")
        print("The pipeline will skip steps that require missing files.\n")

    if args.verify:
        print("\nChecking processed data...")
        proc_ok = verify_processed_data(project_root)
        if proc_ok:
            print("\nAll processed data files present.")
        else:
            print("\nSome processed files missing. Run: python scripts/generate_all_data.py")

        # Also show cache status
        from scripts.data_processing.cache import CacheManager
        cm = CacheManager(project_root)
        print(f"\n{cm.summary()}")
        return

    # --- Set up caching ---
    cache_mgr = None
    if not args.no_cache and not args.force:
        from scripts.data_processing.cache import CacheManager
        cache_mgr = CacheManager(project_root)
        print(f"\nSmart caching: enabled")
    else:
        if args.force:
            # Invalidate cache on --force
            try:
                from scripts.data_processing.cache import CacheManager
                CacheManager(project_root).invalidate()
            except Exception:
                pass
        print(f"\nSmart caching: disabled")

    if n_jobs > 1:
        print(f"Parallel workers: {n_jobs}")

    start_time = time.time()

    # Run pipeline
    from scripts.data_processing import (
        process_boundaries,
        process_firehouses,
        process_precincts,
        process_crashes,
        build_lambda_tables,
        build_distance_matrices,
        run_full_pipeline,
    )

    if args.tier is None:
        run_full_pipeline(
            project_root, force=args.force,
            cache_mgr=cache_mgr, n_jobs=n_jobs,
        )
    elif args.tier == 1:
        process_boundaries(project_root, force=args.force, cache_mgr=cache_mgr)
    elif args.tier == 2:
        process_boundaries(project_root, force=args.force, cache_mgr=cache_mgr)
        process_firehouses(project_root, force=args.force, cache_mgr=cache_mgr)
        process_precincts(project_root, force=args.force, cache_mgr=cache_mgr)
        process_crashes(project_root, force=args.force, cache_mgr=cache_mgr, n_jobs=n_jobs)
    elif args.tier == 3:
        build_lambda_tables(project_root, force=args.force, cache_mgr=cache_mgr)
        build_distance_matrices(project_root, force=args.force, cache_mgr=cache_mgr, n_jobs=n_jobs)

    elapsed = time.time() - start_time

    # --- Generate data manifest ---
    print("\nGenerating data manifest...")
    from scripts.data_processing.versioning import DataVersionManager
    dvm = DataVersionManager(project_root)
    manifest = dvm.create_manifest(seed=args.seed)
    print(f"  Manifest saved to {dvm.manifest_path.name}")
    print(f"  Git commit: {manifest.get('git_commit', 'unknown')}")

    # Final verification
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    verify_processed_data(project_root)

    print(f"\nTotal time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
