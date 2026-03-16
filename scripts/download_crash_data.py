#!/usr/bin/env python3
"""Download Motor Vehicle Collisions crash data from NYC Open Data.

This script downloads the raw crash data CSV that is too large to store
in the Git repository (~536 MB). The data is sourced from:

    https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95

Usage
-----
    python scripts/download_crash_data.py
    python scripts/download_crash_data.py --output data/raw/Motor_Vehicle_Collisions_-_Crashes_20260223.csv
    python scripts/download_crash_data.py --limit 500000   # Download first 500k rows (for testing)
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def download_crash_data(
    output_path: str | Path | None = None,
    limit: int | None = None,
    chunk_size: int = 50000,
) -> Path:
    """Download NYC Motor Vehicle Collisions data via the Socrata Open Data API.

    Parameters
    ----------
    output_path : Path, optional
        Where to save the CSV. Defaults to data/raw/Motor_Vehicle_Collisions_-_Crashes_20260223.csv
    limit : int, optional
        Maximum number of rows to download. None = all rows (~2.2M).
    chunk_size : int
        Number of rows per API request (max 50000 for Socrata).

    Returns
    -------
    Path
        Path to the saved CSV file.
    """
    import pandas as pd
    import requests

    if output_path is None:
        output_path = PROJECT_ROOT / "data" / "raw" / "Motor_Vehicle_Collisions_-_Crashes_20260223.csv"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # NYC Open Data Socrata API endpoint for Motor Vehicle Collisions
    BASE_URL = "https://data.cityofnewyork.us/resource/h9gi-nx95.csv"

    # Use app token if available (higher rate limits), otherwise anonymous
    app_token = os.environ.get("NYC_OPEN_DATA_APP_TOKEN", None)
    headers = {}
    if app_token:
        headers["X-App-Token"] = app_token

    print(f"Downloading NYC Motor Vehicle Collisions data...")
    print(f"  Source: {BASE_URL}")
    print(f"  Output: {output_path}")
    if limit:
        print(f"  Limit:  {limit:,} rows")
    else:
        print(f"  Limit:  all rows (this may take several minutes)")

    offset = 0
    total_rows = 0
    first_chunk = True
    start_time = time.time()

    while True:
        params = {
            "$limit": chunk_size,
            "$offset": offset,
            "$order": "crash_date ASC",
        }
        if limit is not None:
            remaining = limit - total_rows
            if remaining <= 0:
                break
            params["$limit"] = min(chunk_size, remaining)

        try:
            resp = requests.get(BASE_URL, params=params, headers=headers, timeout=120)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"\n  [ERROR] API request failed at offset {offset}: {e}")
            if total_rows > 0:
                print(f"  Partial download saved ({total_rows:,} rows).")
            raise

        # Parse CSV response
        from io import StringIO
        chunk_df = pd.read_csv(StringIO(resp.text))

        if chunk_df.empty:
            break

        # Normalize column names to match expected format
        # Socrata API returns lowercase/underscore names; raw CSV has UPPER CASE
        col_map = {
            "crash_date": "CRASH DATE",
            "crash_time": "CRASH TIME",
            "borough": "BOROUGH",
            "zip_code": "ZIP CODE",
            "latitude": "LATITUDE",
            "longitude": "LONGITUDE",
            "on_street_name": "ON STREET NAME",
            "cross_street_name": "CROSS STREET NAME",
            "off_street_name": "OFF STREET NAME",
            "number_of_persons_injured": "NUMBER OF PERSONS INJURED",
            "number_of_persons_killed": "NUMBER OF PERSONS KILLED",
            "number_of_pedestrians_injured": "NUMBER OF PEDESTRIANS INJURED",
            "number_of_pedestrians_killed": "NUMBER OF PEDESTRIANS KILLED",
            "number_of_cyclist_injured": "NUMBER OF CYCLIST INJURED",
            "number_of_cyclist_killed": "NUMBER OF CYCLIST KILLED",
            "number_of_motorist_injured": "NUMBER OF MOTORIST INJURED",
            "number_of_motorist_killed": "NUMBER OF MOTORIST KILLED",
            "contributing_factor_vehicle_1": "CONTRIBUTING FACTOR VEHICLE 1",
            "contributing_factor_vehicle_2": "CONTRIBUTING FACTOR VEHICLE 2",
            "contributing_factor_vehicle_3": "CONTRIBUTING FACTOR VEHICLE 3",
            "contributing_factor_vehicle_4": "CONTRIBUTING FACTOR VEHICLE 4",
            "contributing_factor_vehicle_5": "CONTRIBUTING FACTOR VEHICLE 5",
            "collision_id": "COLLISION_ID",
            "vehicle_type_code1": "VEHICLE TYPE CODE 1",
            "vehicle_type_code2": "VEHICLE TYPE CODE 2",
            "vehicle_type_code_3": "VEHICLE TYPE CODE 3",
            "vehicle_type_code_4": "VEHICLE TYPE CODE 4",
            "vehicle_type_code_5": "VEHICLE TYPE CODE 5",
            "location": "LOCATION",
        }
        chunk_df.rename(columns={k: v for k, v in col_map.items() if k in chunk_df.columns}, inplace=True)

        # Fix date format: Socrata returns ISO format, raw CSV uses MM/DD/YYYY
        if "CRASH DATE" in chunk_df.columns:
            try:
                chunk_df["CRASH DATE"] = pd.to_datetime(chunk_df["CRASH DATE"]).dt.strftime("%m/%d/%Y")
            except Exception:
                pass

        # Write to file
        chunk_df.to_csv(
            output_path,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
        )
        first_chunk = False

        rows_in_chunk = len(chunk_df)
        total_rows += rows_in_chunk
        offset += rows_in_chunk
        elapsed = time.time() - start_time

        print(f"  Downloaded {total_rows:,} rows... ({elapsed:.0f}s)", end="\r")

        if rows_in_chunk < chunk_size:
            break  # Last page

    elapsed = time.time() - start_time
    file_size_mb = output_path.stat().st_size / 1e6
    print(f"\n  Complete: {total_rows:,} rows, {file_size_mb:.1f} MB in {elapsed:.0f}s")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Download NYC Motor Vehicle Collisions crash data."
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output CSV path. Default: data/raw/Motor_Vehicle_Collisions_-_Crashes_20260223.csv",
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=None,
        help="Maximum rows to download (default: all).",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=50000,
        help="Rows per API request (default: 50000).",
    )
    args = parser.parse_args()

    download_crash_data(
        output_path=args.output,
        limit=args.limit,
        chunk_size=args.chunk_size,
    )


if __name__ == "__main__":
    main()
