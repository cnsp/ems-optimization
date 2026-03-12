#!/usr/bin/env python3
"""Step 4: Audit crash data (chunked processing for large file)"""
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from shapely.geometry import Point
from shapely import prepared
import warnings
warnings.filterwarnings('ignore')

RAW_DIR = Path('/home/ubuntu/ems-optimization/data/raw')
PROCESSED_DIR = Path('/home/ubuntu/ems-optimization/data/processed')

# Load boundaries
with open(RAW_DIR / 'manhattan_geom.pkl', 'rb') as f:
    manhattan_geom = pickle.load(f)
with open(RAW_DIR / 'cbd_geom.pkl', 'rb') as f:
    cbd_geom = pickle.load(f)

# Prepare geometries for faster checking
manhattan_prep = prepared.prep(manhattan_geom)
cbd_prep = prepared.prep(cbd_geom)

NYC_LAT_MIN, NYC_LAT_MAX = 40.5, 41.0
NYC_LON_MIN, NYC_LON_MAX = -74.3, -73.7

print("=== MOTOR VEHICLE COLLISIONS DATA AUDIT ===\n")

# First pass: Get schema and basic stats
print("Reading first chunk for schema analysis...")
sample_df = pd.read_csv(RAW_DIR / 'Motor_Vehicle_Collisions_-_Crashes_20260223.csv', nrows=1000)
print(f"Columns ({len(sample_df.columns)}): {list(sample_df.columns)}")
print(f"\nData types:\n{sample_df.dtypes}")

# Count total rows quickly
print("\nCounting total rows...")
total_rows = sum(1 for _ in open(RAW_DIR / 'Motor_Vehicle_Collisions_-_Crashes_20260223.csv')) - 1
print(f"Total crash records: {total_rows:,}")

# Process in chunks
CHUNK_SIZE = 100000
manhattan_crashes = []
stats = {
    'total_rows': 0,
    'missing_coords': 0,
    'invalid_coords': 0,
    'valid_coords': 0,
    'manhattan_crashes': 0,
    'cbd_crashes': 0,
    'boroughs': {},
    'min_date': None,
    'max_date': None
}

print(f"\nProcessing in chunks of {CHUNK_SIZE:,}...")

for i, chunk in enumerate(pd.read_csv(
    RAW_DIR / 'Motor_Vehicle_Collisions_-_Crashes_20260223.csv',
    chunksize=CHUNK_SIZE,
    low_memory=False
)):
    stats['total_rows'] += len(chunk)
    
    # Parse dates
    chunk['crash_datetime'] = pd.to_datetime(
        chunk['CRASH DATE'] + ' ' + chunk['CRASH TIME'].fillna('00:00'),
        errors='coerce'
    )
    
    # Track date range
    chunk_min = chunk['crash_datetime'].min()
    chunk_max = chunk['crash_datetime'].max()
    if stats['min_date'] is None or chunk_min < stats['min_date']:
        stats['min_date'] = chunk_min
    if stats['max_date'] is None or chunk_max > stats['max_date']:
        stats['max_date'] = chunk_max
    
    # Missing coords
    missing = chunk['LATITUDE'].isna() | chunk['LONGITUDE'].isna()
    stats['missing_coords'] += missing.sum()
    
    # Valid coords
    valid = (
        ~missing &
        (chunk['LATITUDE'] >= NYC_LAT_MIN) & (chunk['LATITUDE'] <= NYC_LAT_MAX) &
        (chunk['LONGITUDE'] >= NYC_LON_MIN) & (chunk['LONGITUDE'] <= NYC_LON_MAX)
    )
    stats['valid_coords'] += valid.sum()
    stats['invalid_coords'] += (~missing & ~valid).sum()
    
    # Borough counts
    for boro, count in chunk['BOROUGH'].value_counts(dropna=False).items():
        boro_key = boro if pd.notna(boro) else 'MISSING'
        stats['boroughs'][boro_key] = stats['boroughs'].get(boro_key, 0) + count
    
    # Filter to valid coords
    valid_chunk = chunk[valid].copy()
    
    # Check Manhattan membership
    def check_manhattan(row):
        pt = Point(row['LONGITUDE'], row['LATITUDE'])
        return manhattan_prep.contains(pt)
    
    def check_cbd(row):
        pt = Point(row['LONGITUDE'], row['LATITUDE'])
        return cbd_prep.contains(pt)
    
    valid_chunk['in_manhattan'] = valid_chunk.apply(check_manhattan, axis=1)
    manhattan_chunk = valid_chunk[valid_chunk['in_manhattan']].copy()
    
    if len(manhattan_chunk) > 0:
        manhattan_chunk['in_cbd'] = manhattan_chunk.apply(check_cbd, axis=1)
        stats['manhattan_crashes'] += len(manhattan_chunk)
        stats['cbd_crashes'] += manhattan_chunk['in_cbd'].sum()
        manhattan_crashes.append(manhattan_chunk)
    
    print(f"  Chunk {i+1}: {len(chunk):,} rows, {len(manhattan_chunk):,} Manhattan crashes")

# Combine Manhattan crashes
print("\nCombining Manhattan crashes...")
manhattan_df = pd.concat(manhattan_crashes, ignore_index=True)
manhattan_df = manhattan_df.drop(columns=['in_manhattan'])

# Save
manhattan_df.to_csv(PROCESSED_DIR / 'crashes_manhattan.csv', index=False)
manhattan_df.to_parquet(PROCESSED_DIR / 'crashes_manhattan.parquet', index=False)

print("\n" + "=" * 60)
print("CRASH DATA AUDIT SUMMARY")
print("=" * 60)
print(f"Total records: {stats['total_rows']:,}")
print(f"Date range: {stats['min_date']} to {stats['max_date']}")
print(f"\nCoordinate quality:")
print(f"  Valid NYC coords: {stats['valid_coords']:,} ({stats['valid_coords']/stats['total_rows']*100:.1f}%)")
print(f"  Missing coords: {stats['missing_coords']:,} ({stats['missing_coords']/stats['total_rows']*100:.1f}%)")
print(f"  Invalid coords: {stats['invalid_coords']:,} ({stats['invalid_coords']/stats['total_rows']*100:.1f}%)")
print(f"\nBorough distribution:")
for boro, count in sorted(stats['boroughs'].items(), key=lambda x: -x[1]):
    print(f"  {boro}: {count:,}")
print(f"\nManhattan crashes: {stats['manhattan_crashes']:,}")
print(f"CBD crashes: {stats['cbd_crashes']:,} ({stats['cbd_crashes']/stats['manhattan_crashes']*100:.1f}% of Manhattan)")
print(f"\nSaved: crashes_manhattan.csv ({len(manhattan_df):,} records)")
print(f"Saved: crashes_manhattan.parquet")

# Save stats for manifest
import json
with open(PROCESSED_DIR / 'crash_audit_stats.json', 'w') as f:
    json.dump({k: str(v) if isinstance(v, pd.Timestamp) else v for k, v in stats.items()}, f, indent=2)
