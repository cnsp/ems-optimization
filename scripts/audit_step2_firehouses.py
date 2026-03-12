#!/usr/bin/env python3
"""Step 2: Audit firehouse data"""
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import pickle

RAW_DIR = Path('/home/ubuntu/ems-optimization/data/raw')
PROCESSED_DIR = Path('/home/ubuntu/ems-optimization/data/processed')

# Load boundaries
with open(RAW_DIR / 'manhattan_geom.pkl', 'rb') as f:
    manhattan_geom = pickle.load(f)
with open(RAW_DIR / 'cbd_geom.pkl', 'rb') as f:
    cbd_geom = pickle.load(f)

print("=== FDNY FIREHOUSE DATA AUDIT ===\n")

df = pd.read_csv(RAW_DIR / 'FDNY_Firehouse_Listing_20260223.csv')
print(f"Total firehouses: {len(df)}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nSample data:\n{df.head(3)}")

# Missing values
print(f"\nMissing values:")
missing = df.isna().sum()
print(missing[missing > 0] if (missing > 0).any() else "None")

# Find coordinate columns
print(f"\nColumn names with potential coords: {[c for c in df.columns if any(x in c.lower() for x in ['lat', 'lon', 'lng', 'coord'])]}")

# NYC coordinate bounds
NYC_LAT_MIN, NYC_LAT_MAX = 40.5, 41.0
NYC_LON_MIN, NYC_LON_MAX = -74.3, -73.7

# Identify lat/lon columns
lat_col = [c for c in df.columns if 'lat' in c.lower()][0] if any('lat' in c.lower() for c in df.columns) else None
lon_col = [c for c in df.columns if 'lon' in c.lower()][0] if any('lon' in c.lower() for c in df.columns) else None

print(f"\nIdentified coordinate columns: lat={lat_col}, lon={lon_col}")

if lat_col and lon_col:
    # Validate coordinates
    valid = (
        df[lat_col].notna() & df[lon_col].notna() &
        (df[lat_col] >= NYC_LAT_MIN) & (df[lat_col] <= NYC_LAT_MAX) &
        (df[lon_col] >= NYC_LON_MIN) & (df[lon_col] <= NYC_LON_MAX)
    )
    print(f"Valid NYC coordinates: {valid.sum()}/{len(df)}")
    
    # Create GeoDataFrame
    df_valid = df[valid].copy()
    geometry = [Point(xy) for xy in zip(df_valid[lon_col], df_valid[lat_col])]
    gdf = gpd.GeoDataFrame(df_valid, geometry=geometry, crs='EPSG:4326')
    
    # Check Manhattan/CBD
    gdf['in_manhattan'] = gdf.within(manhattan_geom)
    gdf['in_cbd'] = gdf.within(cbd_geom)
    
    print(f"\nFirehouses in Manhattan: {gdf['in_manhattan'].sum()}")
    print(f"Firehouses in CBD: {gdf['in_cbd'].sum()}")
    
    # Borough distribution
    boro_cols = [c for c in df.columns if 'boro' in c.lower()]
    if boro_cols:
        print(f"\nBorough distribution (from {boro_cols[0]}):")
        print(df[boro_cols[0]].value_counts())
    
    # Save cleaned data
    clean_df = gdf.drop(columns=['geometry'])
    clean_df.to_csv(PROCESSED_DIR / 'firehouses_clean.csv', index=False)
    print(f"\nSaved: firehouses_clean.csv ({len(clean_df)} records)")
    
    # Manhattan only
    manhattan_fh = gdf[gdf['in_manhattan']].drop(columns=['geometry'])
    manhattan_fh.to_csv(PROCESSED_DIR / 'firehouses_manhattan.csv', index=False)
    print(f"Saved: firehouses_manhattan.csv ({len(manhattan_fh)} records)")
