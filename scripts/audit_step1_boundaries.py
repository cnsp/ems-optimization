#!/usr/bin/env python3
"""Step 1: Audit geographic boundaries"""
import geopandas as gpd
from pathlib import Path

RAW_DIR = Path('/home/ubuntu/ems-optimization/data/raw')

print("=== GEOGRAPHIC BOUNDARIES AUDIT ===\n")

# Load Manhattan boundary
manhattan_gdf = gpd.read_file(RAW_DIR / 'manhattan_boundary.geojson')
print(f"Manhattan boundary:")
print(f"  Features: {len(manhattan_gdf)}")
print(f"  CRS: {manhattan_gdf.crs}")
print(f"  Bounds: {manhattan_gdf.total_bounds}")
print(f"  Area (sq km): {manhattan_gdf.to_crs('EPSG:2263').area.sum() / 1e6:.2f}")

# Load CBD boundary
cbd_gdf = gpd.read_file(RAW_DIR / 'cbd_boundary.geojson')
print(f"\nCBD boundary:")
print(f"  Features: {len(cbd_gdf)}")
print(f"  CRS: {cbd_gdf.crs}")
print(f"  Bounds: {cbd_gdf.total_bounds}")
print(f"  Area (sq km): {cbd_gdf.to_crs('EPSG:2263').area.sum() / 1e6:.2f}")

# Check CBD subset
manhattan_geom = manhattan_gdf.unary_union
cbd_geom = cbd_gdf.unary_union
overlap = manhattan_geom.intersection(cbd_geom).area / cbd_geom.area * 100
print(f"\nCBD overlap with Manhattan: {overlap:.2f}%")

# Save geometries as pickle for later use
import pickle
with open(RAW_DIR / 'manhattan_geom.pkl', 'wb') as f:
    pickle.dump(manhattan_geom, f)
with open(RAW_DIR / 'cbd_geom.pkl', 'wb') as f:
    pickle.dump(cbd_geom, f)
print("\nSaved geometry pickles for faster loading")
