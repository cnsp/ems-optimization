#!/usr/bin/env python3
"""Step 3: Audit police precincts data"""
import pandas as pd
import geopandas as gpd
from shapely import wkt
from pathlib import Path
import pickle

RAW_DIR = Path('/home/ubuntu/ems-optimization/data/raw')
PROCESSED_DIR = Path('/home/ubuntu/ems-optimization/data/processed')

# Load boundaries
with open(RAW_DIR / 'manhattan_geom.pkl', 'rb') as f:
    manhattan_geom = pickle.load(f)

print("=== POLICE PRECINCTS DATA AUDIT ===\n")

df = pd.read_csv(RAW_DIR / 'Police_Precincts_20260223.csv')
print(f"Total precincts: {len(df)}")
print(f"\nColumns: {list(df.columns)}")

# Find geometry column
geom_cols = [c for c in df.columns if 'geom' in c.lower() or 'wkt' in c.lower()]
print(f"Geometry columns: {geom_cols}")

# Sample non-geometry data
non_geom_cols = [c for c in df.columns if c not in geom_cols]
print(f"\nSample data (non-geometry columns):\n{df[non_geom_cols].head()}")

# Convert to GeoDataFrame
geom_col = 'the_geom' if 'the_geom' in df.columns else geom_cols[0]
print(f"\nUsing geometry column: {geom_col}")

df['geometry'] = df[geom_col].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

# Validate geometries
print(f"\nGeometry validation:")
print(f"  Invalid geometries: {(~gdf.geometry.is_valid).sum()}")
print(f"  Empty geometries: {gdf.geometry.is_empty.sum()}")

# Identify Manhattan precincts
gdf['in_manhattan'] = gdf.geometry.intersects(manhattan_geom)
manhattan_precincts = gdf[gdf['in_manhattan']].copy()

print(f"\nPrecincts intersecting Manhattan: {len(manhattan_precincts)}")

# Get precinct numbers
precinct_col = [c for c in gdf.columns if 'precinct' in c.lower()][0]
print(f"Manhattan precinct numbers ({precinct_col}):")
print(sorted(manhattan_precincts[precinct_col].tolist()))

# Save Manhattan precincts
manhattan_precincts_save = manhattan_precincts.drop(columns=[geom_col])
manhattan_precincts_save.to_file(PROCESSED_DIR / 'precincts_manhattan.geojson', driver='GeoJSON')
print(f"\nSaved: precincts_manhattan.geojson ({len(manhattan_precincts_save)} precincts)")
