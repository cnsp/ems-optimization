#!/usr/bin/env python3
"""
Comprehensive Data Audit for EMS Optimization Project
Phase 1: Data validation, cleaning, and Manhattan filtering
"""

import pandas as pd
import geopandas as gpd
import json
from pathlib import Path
from shapely.geometry import Point, shape
import warnings
warnings.filterwarnings('ignore')

# Paths
RAW_DIR = Path('/home/ubuntu/ems-optimization/data/raw')
PROCESSED_DIR = Path('/home/ubuntu/ems-optimization/data/processed')
MANIFEST_DIR = Path('/home/ubuntu/ems-optimization/data/manifests')

# NYC coordinate bounds
NYC_LAT_MIN, NYC_LAT_MAX = 40.5, 41.0
NYC_LON_MIN, NYC_LON_MAX = -74.3, -73.7

audit_results = []

print("=" * 80)
print("EMS OPTIMIZATION PROJECT - DATA AUDIT")
print("=" * 80)

# ============================================================================
# 1. GEOGRAPHIC BOUNDARIES
# ============================================================================
print("\n### 1. GEOGRAPHIC BOUNDARIES ###\n")

# Load Manhattan boundary
manhattan_gdf = gpd.read_file(RAW_DIR / 'manhattan_boundary.geojson')
print(f"Manhattan boundary loaded: {len(manhattan_gdf)} feature(s)")
print(f"  CRS: {manhattan_gdf.crs}")
print(f"  Bounds: {manhattan_gdf.total_bounds}")
manhattan_geom = manhattan_gdf.unary_union

# Load CBD boundary
cbd_gdf = gpd.read_file(RAW_DIR / 'cbd_boundary.geojson')
print(f"\nCBD boundary loaded: {len(cbd_gdf)} feature(s)")
print(f"  CRS: {cbd_gdf.crs}")
print(f"  Bounds: {cbd_gdf.total_bounds}")
cbd_geom = cbd_gdf.unary_union

# Check CBD is subset of Manhattan
cbd_in_manhattan = manhattan_geom.contains(cbd_geom) or cbd_geom.within(manhattan_geom)
cbd_intersection = manhattan_geom.intersection(cbd_geom).area / cbd_geom.area * 100
print(f"\nCBD fully within Manhattan: {cbd_in_manhattan}")
print(f"CBD overlap with Manhattan: {cbd_intersection:.2f}%")

audit_results.append({
    'file': 'manhattan_boundary.geojson',
    'rows': len(manhattan_gdf),
    'valid': True,
    'notes': f'CRS: {manhattan_gdf.crs}'
})
audit_results.append({
    'file': 'cbd_boundary.geojson',
    'rows': len(cbd_gdf),
    'valid': True,
    'notes': f'CBD overlap with Manhattan: {cbd_intersection:.1f}%'
})

# ============================================================================
# 2. CRASH DATA
# ============================================================================
print("\n" + "=" * 80)
print("### 2. MOTOR VEHICLE COLLISIONS DATA ###")
print("=" * 80)

# Load crash data
print("\nLoading crash data (this may take a moment)...")
crashes_df = pd.read_csv(RAW_DIR / 'Motor_Vehicle_Collisions_-_Crashes_20260223.csv', low_memory=False)
print(f"\nTotal crash records: {len(crashes_df):,}")
print(f"Columns ({len(crashes_df.columns)}): {list(crashes_df.columns)}")

# Schema and dtypes
print("\n--- Data Types ---")
print(crashes_df.dtypes.to_string())

# Date range
print("\n--- Date Analysis ---")
date_col = 'CRASH DATE' if 'CRASH DATE' in crashes_df.columns else None
time_col = 'CRASH TIME' if 'CRASH TIME' in crashes_df.columns else None

if date_col:
    crashes_df['crash_datetime'] = pd.to_datetime(
        crashes_df[date_col] + ' ' + crashes_df[time_col].fillna('00:00'),
        errors='coerce'
    )
    valid_dates = crashes_df['crash_datetime'].notna()
    print(f"Valid datetime records: {valid_dates.sum():,} ({valid_dates.mean()*100:.2f}%)")
    print(f"Date range: {crashes_df['crash_datetime'].min()} to {crashes_df['crash_datetime'].max()}")

# Missing values in critical columns
print("\n--- Missing Values in Critical Columns ---")
critical_cols = ['LATITUDE', 'LONGITUDE', 'CRASH DATE', 'CRASH TIME', 'BOROUGH']
for col in critical_cols:
    if col in crashes_df.columns:
        missing = crashes_df[col].isna().sum()
        pct = missing / len(crashes_df) * 100
        print(f"  {col}: {missing:,} missing ({pct:.2f}%)")

# Coordinate validation
print("\n--- Coordinate Validation ---")
lat_col = 'LATITUDE'
lon_col = 'LONGITUDE'

valid_coords = (
    crashes_df[lat_col].notna() & 
    crashes_df[lon_col].notna() &
    (crashes_df[lat_col] >= NYC_LAT_MIN) & (crashes_df[lat_col] <= NYC_LAT_MAX) &
    (crashes_df[lon_col] >= NYC_LON_MIN) & (crashes_df[lon_col] <= NYC_LON_MAX)
)
print(f"Records with valid NYC coordinates: {valid_coords.sum():,} ({valid_coords.mean()*100:.2f}%)")

# Borough distribution
print("\n--- Borough Distribution ---")
borough_counts = crashes_df['BOROUGH'].value_counts(dropna=False)
print(borough_counts.to_string())

# Filter to Manhattan using geometry
print("\n--- Filtering to Manhattan ---")
crashes_with_coords = crashes_df[valid_coords].copy()
print(f"Records with valid coords: {len(crashes_with_coords):,}")

# Create GeoDataFrame for spatial filtering
geometry = [Point(xy) for xy in zip(crashes_with_coords[lon_col], crashes_with_coords[lat_col])]
crashes_gdf = gpd.GeoDataFrame(crashes_with_coords, geometry=geometry, crs='EPSG:4326')

# Spatial join with Manhattan
manhattan_crashes = crashes_gdf[crashes_gdf.within(manhattan_geom)].copy()
print(f"Crashes within Manhattan boundary: {len(manhattan_crashes):,}")

# Also tag CBD crashes
manhattan_crashes['in_cbd'] = manhattan_crashes.within(cbd_geom)
cbd_count = manhattan_crashes['in_cbd'].sum()
print(f"  - Of which in CBD: {cbd_count:,} ({cbd_count/len(manhattan_crashes)*100:.1f}%)")

# Drop geometry column for CSV export
manhattan_crashes_export = manhattan_crashes.drop(columns=['geometry']).copy()

# Save Manhattan crashes
manhattan_crashes_export.to_csv(PROCESSED_DIR / 'crashes_manhattan.csv', index=False)
print(f"\nSaved: crashes_manhattan.csv ({len(manhattan_crashes_export):,} records)")

# Also save as parquet for efficiency
manhattan_crashes_export.to_parquet(PROCESSED_DIR / 'crashes_manhattan.parquet', index=False)
print(f"Saved: crashes_manhattan.parquet")

audit_results.append({
    'file': 'Motor_Vehicle_Collisions_-_Crashes_20260223.csv',
    'rows': len(crashes_df),
    'valid': True,
    'notes': f'Date range: {crashes_df["crash_datetime"].min().date()} to {crashes_df["crash_datetime"].max().date()}'
})
audit_results.append({
    'file': 'crashes_manhattan.csv (processed)',
    'rows': len(manhattan_crashes_export),
    'valid': True,
    'notes': f'{cbd_count} in CBD ({cbd_count/len(manhattan_crashes_export)*100:.1f}%)'
})

# ============================================================================
# 3. FIREHOUSE DATA
# ============================================================================
print("\n" + "=" * 80)
print("### 3. FDNY FIREHOUSE DATA ###")
print("=" * 80)

firehouses_df = pd.read_csv(RAW_DIR / 'FDNY_Firehouse_Listing_20260223.csv')
print(f"\nTotal firehouses: {len(firehouses_df):,}")
print(f"Columns: {list(firehouses_df.columns)}")

print("\n--- Data Types ---")
print(firehouses_df.dtypes.to_string())

# Find coordinate columns
lat_cols = [c for c in firehouses_df.columns if 'lat' in c.lower()]
lon_cols = [c for c in firehouses_df.columns if 'lon' in c.lower() or 'lng' in c.lower()]
print(f"\nLatitude columns found: {lat_cols}")
print(f"Longitude columns found: {lon_cols}")

# Check for coordinates
if lat_cols and lon_cols:
    fh_lat = lat_cols[0]
    fh_lon = lon_cols[0]
else:
    # Check for combined location column
    print("\nLooking for location data in other columns...")
    print(firehouses_df.head(2).to_string())

# Sample data
print("\n--- Sample Data ---")
print(firehouses_df.head().to_string())

# Check for missing values
print("\n--- Missing Values ---")
missing = firehouses_df.isna().sum()
print(missing[missing > 0].to_string() if (missing > 0).any() else "No missing values")

# Determine coordinate columns from data inspection
if 'Latitude' in firehouses_df.columns:
    fh_lat, fh_lon = 'Latitude', 'Longitude'
elif 'latitude' in firehouses_df.columns:
    fh_lat, fh_lon = 'latitude', 'longitude'
else:
    # Check column names more carefully
    print("Column names:", firehouses_df.columns.tolist())

# Validate coordinates
print("\n--- Coordinate Validation ---")
valid_fh_coords = (
    firehouses_df[fh_lat].notna() & 
    firehouses_df[fh_lon].notna() &
    (firehouses_df[fh_lat] >= NYC_LAT_MIN) & (firehouses_df[fh_lat] <= NYC_LAT_MAX) &
    (firehouses_df[fh_lon] >= NYC_LON_MIN) & (firehouses_df[fh_lon] <= NYC_LON_MAX)
)
print(f"Firehouses with valid NYC coordinates: {valid_fh_coords.sum()}/{len(firehouses_df)}")

# Create GeoDataFrame and check Manhattan
firehouses_valid = firehouses_df[valid_fh_coords].copy()
fh_geometry = [Point(xy) for xy in zip(firehouses_valid[fh_lon], firehouses_valid[fh_lat])]
firehouses_gdf = gpd.GeoDataFrame(firehouses_valid, geometry=fh_geometry, crs='EPSG:4326')

firehouses_gdf['in_manhattan'] = firehouses_gdf.within(manhattan_geom)
firehouses_gdf['in_cbd'] = firehouses_gdf.within(cbd_geom)

manhattan_fh = firehouses_gdf['in_manhattan'].sum()
cbd_fh = firehouses_gdf['in_cbd'].sum()
print(f"Firehouses in Manhattan: {manhattan_fh}")
print(f"Firehouses in CBD: {cbd_fh}")

# Borough distribution if available
if 'Borough' in firehouses_df.columns or 'FacilityBoro' in firehouses_df.columns:
    boro_col = 'Borough' if 'Borough' in firehouses_df.columns else 'FacilityBoro'
    print(f"\n--- Firehouse Borough Distribution (from {boro_col}) ---")
    print(firehouses_df[boro_col].value_counts().to_string())

# Save cleaned firehouse data
firehouses_clean = firehouses_gdf.drop(columns=['geometry']).copy()
firehouses_clean.to_csv(PROCESSED_DIR / 'firehouses_clean.csv', index=False)
print(f"\nSaved: firehouses_clean.csv ({len(firehouses_clean)} records)")

audit_results.append({
    'file': 'FDNY_Firehouse_Listing_20260223.csv',
    'rows': len(firehouses_df),
    'valid': True,
    'notes': f'{manhattan_fh} in Manhattan, {cbd_fh} in CBD'
})

# ============================================================================
# 4. POLICE PRECINCTS DATA
# ============================================================================
print("\n" + "=" * 80)
print("### 4. POLICE PRECINCTS DATA ###")
print("=" * 80)

precincts_df = pd.read_csv(RAW_DIR / 'Police_Precincts_20260223.csv')
print(f"\nTotal precincts: {len(precincts_df):,}")
print(f"Columns: {list(precincts_df.columns)}")

print("\n--- Sample Data ---")
print(precincts_df.head(3).to_string())

# Check for geometry column
geom_col = None
for col in precincts_df.columns:
    if 'geom' in col.lower() or 'the_geom' in col.lower() or 'wkt' in col.lower():
        geom_col = col
        break

print(f"\n--- Geometry column: {geom_col} ---")
if geom_col:
    # Convert to GeoDataFrame
    from shapely import wkt
    precincts_df['geometry'] = precincts_df[geom_col].apply(wkt.loads)
    precincts_gdf = gpd.GeoDataFrame(precincts_df, geometry='geometry', crs='EPSG:4326')
    
    # Validate geometries
    invalid_geoms = ~precincts_gdf.geometry.is_valid
    print(f"Invalid geometries: {invalid_geoms.sum()}")
    
    # Find Manhattan precincts
    precincts_gdf['in_manhattan'] = precincts_gdf.geometry.intersects(manhattan_geom)
    manhattan_precincts = precincts_gdf[precincts_gdf['in_manhattan']].copy()
    print(f"Precincts intersecting Manhattan: {len(manhattan_precincts)}")
    
    # Identify precinct numbers if available
    precinct_col = None
    for col in ['Precinct', 'precinct', 'PRECINCT', 'precinct_n']:
        if col in precincts_gdf.columns:
            precinct_col = col
            break
    
    if precinct_col:
        print(f"Manhattan precinct numbers: {sorted(manhattan_precincts[precinct_col].tolist())}")
    
    # Save Manhattan precincts
    manhattan_precincts_save = manhattan_precincts.drop(columns=[geom_col], errors='ignore')
    manhattan_precincts_save.to_file(PROCESSED_DIR / 'precincts_manhattan.geojson', driver='GeoJSON')
    print(f"\nSaved: precincts_manhattan.geojson ({len(manhattan_precincts)} precincts)")
    
    audit_results.append({
        'file': 'Police_Precincts_20260223.csv',
        'rows': len(precincts_df),
        'valid': invalid_geoms.sum() == 0,
        'notes': f'{len(manhattan_precincts)} Manhattan precincts'
    })

# ============================================================================
# 5. SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("### DATA AUDIT SUMMARY ###")
print("=" * 80)

# Save audit summary
audit_df = pd.DataFrame(audit_results)
audit_df.to_csv(MANIFEST_DIR / 'data_audit_summary.csv', index=False)
print("\nAudit summary saved to: data/manifests/data_audit_summary.csv")
print(audit_df.to_string(index=False))

# Data quality issues
print("\n--- Data Quality Issues Found ---")
issues = []
issues.append(f"Crash data: {(~valid_coords).sum():,} records ({(~valid_coords).mean()*100:.1f}%) missing/invalid coordinates")
issues.append(f"Crash data: Borough field has {crashes_df['BOROUGH'].isna().sum():,} missing values")

for issue in issues:
    print(f"  • {issue}")

print("\n" + "=" * 80)
print("DATA AUDIT COMPLETE")
print("=" * 80)
