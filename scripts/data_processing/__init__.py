"""
Data processing pipeline functions for EMS Optimization.

This module provides idempotent functions for each tier of the data
processing DAG.  Each function checks whether its outputs already exist
and regenerates them only when necessary (or when force=True).

Tier 1: Geometry pickles       (boundaries -> pkl)
Tier 2: Spatial filtering      (raw data + pkl -> Manhattan subsets)
Tier 3: Demand modeling        (Manhattan crashes -> lambda tables)
Tier 3: Distance matrices      (firehouses + precincts -> distance CSVs)

Usage
-----
    from scripts.data_processing import (
        process_boundaries,
        process_firehouses,
        process_precincts,
        process_crashes,
        build_lambda_tables,
        build_distance_matrices,
        run_full_pipeline,
    )
"""

from scripts.data_processing.tier1_boundaries import process_boundaries
from scripts.data_processing.tier2_firehouses import process_firehouses
from scripts.data_processing.tier2_precincts import process_precincts
from scripts.data_processing.tier2_crashes import process_crashes
from scripts.data_processing.tier3_demand import build_lambda_tables
from scripts.data_processing.tier3_distance import build_distance_matrices


def run_full_pipeline(project_root, force=False):
    """Run all data processing tiers in order.
    
    Parameters
    ----------
    project_root : str or Path
        Path to the project root directory.
    force : bool
        If True, regenerate all files even if they already exist.
    
    Returns
    -------
    dict
        Summary of what was generated.
    """
    from pathlib import Path
    project_root = Path(project_root)
    
    summary = {}
    
    print("=" * 60)
    print("EMS DATA PROCESSING PIPELINE")
    print("=" * 60)
    
    print("\n--- Tier 1: Geographic Boundaries ---")
    summary["tier1"] = process_boundaries(project_root, force=force)
    
    print("\n--- Tier 2a: Firehouses ---")
    summary["tier2_firehouses"] = process_firehouses(project_root, force=force)
    
    print("\n--- Tier 2b: Precincts ---")
    summary["tier2_precincts"] = process_precincts(project_root, force=force)
    
    print("\n--- Tier 2c: Crashes ---")
    summary["tier2_crashes"] = process_crashes(project_root, force=force)
    
    print("\n--- Tier 3a: Demand Lambda Tables ---")
    summary["tier3_demand"] = build_lambda_tables(project_root, force=force)
    
    print("\n--- Tier 3b: Distance Matrices ---")
    summary["tier3_distance"] = build_distance_matrices(project_root, force=force)
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    
    return summary


__all__ = [
    "process_boundaries",
    "process_firehouses",
    "process_precincts",
    "process_crashes",
    "build_lambda_tables",
    "build_distance_matrices",
    "run_full_pipeline",
]
