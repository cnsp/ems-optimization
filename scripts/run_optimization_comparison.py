#!/usr/bin/env python3
"""
EMS Optimization - Policy Generation and Comparison
Phase 3: Generate allocation policies and compare performance
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import json
import warnings
warnings.filterwarnings('ignore')

from ems_readiness.optimization.allocator import EMSAllocator

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 11

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / 'results' / 'optimization'
MAPS_DIR = BASE_DIR / 'results' / 'maps'
FIGURES_DIR = BASE_DIR / 'results' / 'figures'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'

print("=" * 80)
print("EMS OPTIMIZATION - POLICY GENERATION AND COMPARISON")
print("=" * 80)

# ============================================================================
# 1. INITIALIZE ALLOCATOR
# ============================================================================
print("\n### 1. INITIALIZING ALLOCATOR ###\n")

allocator = EMSAllocator.from_project(BASE_DIR)
print(f"Loaded data:")
print(f"  - Firehouses: {len(allocator.distance_matrix.index)}")
print(f"  - Precincts: {len(allocator.demand)}")
print(f"  - Travel speed: {allocator.travel_speed_mph} mph")
print(f"  - Total demand: {allocator.demand.sum():.2f} crashes/hour")

# ============================================================================
# 2. RUN OPTIMIZATIONS FOR MULTIPLE SCENARIOS
# ============================================================================
print("\n" + "=" * 80)
print("### 2. RUNNING OPTIMIZATIONS ###")
print("=" * 80)

K_VALUES = [20, 30, 40, 48]
CAPACITY = 5
COVERAGE_THRESHOLD = 8.0  # minutes

# Policy definitions
POLICIES = {
    'P0': {'name': 'Spatially-Stratified Uniform', 'type': 'baseline'},
    'P1': {'name': 'Demand-Proportional', 'type': 'baseline'},
    'P2': {'name': 'Demand-Weighted Optimized', 'type': 'demand_weighted'},
    'P2b': {'name': 'P-Median Optimized', 'type': 'p_median'},
    'P2c': {'name': 'Maximal Coverage', 'type': 'maximal_coverage'},
}

all_results = []
allocation_tables = {}

for K in K_VALUES:
    print(f"\n--- K = {K} units ---")
    allocation_tables[K] = []
    
    for policy_id, policy_info in POLICIES.items():
        print(f"  Running {policy_id} ({policy_info['name']})...", end=' ')
        
        if policy_info['type'] == 'baseline':
            if policy_id == 'P0':
                result = allocator.baseline_p0(K, CAPACITY)
            else:  # P1
                result = allocator.baseline_demand_proportional(K, CAPACITY)
        else:
            result = allocator.solve(
                model=policy_info['type'],
                K=K,
                capacity=CAPACITY,
                coverage_threshold=COVERAGE_THRESHOLD,
                solver_time_limit=300,
            )
        
        # Compute performance metrics
        coverage_metrics = allocator.evaluate_coverage(result.allocation, COVERAGE_THRESHOLD)
        
        # Response time (already in result.objective_value)
        response_time = result.objective_value
        
        # Additional metrics
        num_firehouses = result.active_firehouses
        max_units = int(result.allocation.max())
        
        # Store results
        record = {
            'K': K,
            'policy_id': policy_id,
            'policy_name': policy_info['name'],
            'model_type': policy_info['type'],
            'status': result.status,
            'response_time': round(response_time, 4),
            'covered_precincts': coverage_metrics['covered_precincts'],
            'total_precincts': coverage_metrics['total_precincts'],
            'pct_precincts_covered': coverage_metrics['pct_precincts'],
            'pct_demand_covered': coverage_metrics['covered_demand_pct'],
            'num_firehouses_used': num_firehouses,
            'max_units_at_firehouse': max_units,
            'solve_time_sec': result.solve_time_sec,
        }
        all_results.append(record)
        
        # Store allocation for this K
        alloc_df = result.allocation.to_frame('units')
        alloc_df['policy'] = policy_id
        alloc_df['K'] = K
        alloc_reset = alloc_df.reset_index()
        alloc_reset.columns = ['firehouse' if c not in ('units', 'policy', 'K') else c for c in alloc_reset.columns]
        allocation_tables[K].append(alloc_reset)
        
        print(f"✓ (Response time: {response_time:.2f}, Coverage: {coverage_metrics['covered_demand_pct']:.1f}%)")
    
    # Save allocation table for this K
    K_table = pd.concat(allocation_tables[K], ignore_index=True)
    K_table_pivot = K_table.pivot_table(index='firehouse', columns='policy', values='units', aggfunc='first')
    K_table_pivot.to_csv(RESULTS_DIR / f'allocations_K{K}.csv')
    print(f"\nSaved: allocations_K{K}.csv")

# ============================================================================
# 3. CREATE COMPARISON TABLES
# ============================================================================
print("\n" + "=" * 80)
print("### 3. CREATING COMPARISON TABLES ###")
print("=" * 80)

results_df = pd.DataFrame(all_results)

# Policy comparison table
print("\nPolicy Comparison Table:")
print(results_df.to_string(index=False))

# Save full comparison
results_df.to_csv(RESULTS_DIR / 'policy_comparison.csv', index=False)
print(f"\nSaved: policy_comparison.csv")

# Sensitivity analysis (how performance changes with K)
sensitivity = results_df.pivot_table(
    index='K',
    columns='policy_id',
    values=['response_time', 'pct_demand_covered']
).round(2)
sensitivity.to_csv(RESULTS_DIR / 'sensitivity_analysis.csv')
print(f"Saved: sensitivity_analysis.csv")

# Summary table for report
summary = results_df.groupby('policy_id').agg({
    'response_time': 'mean',
    'pct_demand_covered': 'mean',
    'num_firehouses_used': 'mean',
    'solve_time_sec': 'mean',
}).round(2)
summary['policy_name'] = [POLICIES[p]['name'] for p in summary.index]
summary = summary[['policy_name', 'response_time', 'pct_demand_covered', 
                    'num_firehouses_used', 'solve_time_sec']]
print("\nAverage Performance Across All K:")
print(summary.to_string())

# ============================================================================
# 4. CREATE COMPARISON VISUALIZATIONS
# ============================================================================
print("\n" + "=" * 80)
print("### 4. CREATING COMPARISON VISUALIZATIONS ###")
print("=" * 80)

# Figure 1: Response time vs K for each policy
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Response time vs K
ax = axes[0, 0]
for policy_id in ['P0', 'P1', 'P2', 'P2b', 'P2c']:
    data = results_df[results_df['policy_id'] == policy_id]
    ax.plot(data['K'], data['response_time'], 'o-', 
            label=POLICIES[policy_id]['name'], linewidth=2, markersize=8)
ax.set_xlabel('Number of Units (K)')
ax.set_ylabel('Expected Response Time (minutes)')
ax.set_title('Response Time vs Unit Count')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Coverage vs K
ax = axes[0, 1]
for policy_id in ['P0', 'P1', 'P2', 'P2b', 'P2c']:
    data = results_df[results_df['policy_id'] == policy_id]
    ax.plot(data['K'], data['pct_demand_covered'], 'o-', 
            label=POLICIES[policy_id]['name'], linewidth=2, markersize=8)
ax.set_xlabel('Number of Units (K)')
ax.set_ylabel('% Demand Covered (≤8 min)')
ax.set_title('Coverage vs Unit Count')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Firehouses used vs K
ax = axes[1, 0]
for policy_id in ['P0', 'P1', 'P2', 'P2b', 'P2c']:
    data = results_df[results_df['policy_id'] == policy_id]
    ax.plot(data['K'], data['num_firehouses_used'], 'o-', 
            label=POLICIES[policy_id]['name'], linewidth=2, markersize=8)
ax.set_xlabel('Number of Units (K)')
ax.set_ylabel('Number of Firehouses Used')
ax.set_title('Firehouses Used vs Unit Count')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Performance comparison at K=40
ax = axes[1, 1]
K40_data = results_df[results_df['K'] == 40].set_index('policy_id')
x_pos = np.arange(len(K40_data))
width = 0.35

bars1 = ax.bar(x_pos - width/2, K40_data['response_time'], width, 
               label='Response Time (min)', alpha=0.8, color='steelblue')
ax2 = ax.twinx()
bars2 = ax2.bar(x_pos + width/2, K40_data['pct_demand_covered'], width, 
                label='% Covered', alpha=0.8, color='darkorange')

ax.set_xlabel('Policy')
ax.set_ylabel('Response Time (minutes)', color='steelblue')
ax2.set_ylabel('% Demand Covered', color='darkorange')
ax.set_title('Performance Comparison at K=40')
ax.set_xticks(x_pos)
ax.set_xticklabels(K40_data.index)
ax.tick_params(axis='y', labelcolor='steelblue')
ax2.tick_params(axis='y', labelcolor='darkorange')

# Combined legend
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
plt.savefig(FIGURES_DIR / 'fig_policy_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: fig_policy_comparison.png")

# Figure 2: Trade-off curve
fig, ax = plt.subplots(figsize=(10, 6))
for K in K_VALUES:
    K_data = results_df[results_df['K'] == K]
    ax.scatter(K_data['response_time'], K_data['pct_demand_covered'], 
               s=150, alpha=0.7, label=f'K={K}')
    
    # Label each point with policy
    for _, row in K_data.iterrows():
        ax.annotate(row['policy_id'], 
                    (row['response_time'], row['pct_demand_covered']),
                    fontsize=9, ha='right', va='bottom')

ax.set_xlabel('Expected Response Time (minutes)')
ax.set_ylabel('% Demand Covered (≤8 min)')
ax.set_title('Response Time vs Coverage Trade-off')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'fig_tradeoff_curve.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: fig_tradeoff_curve.png")

# ============================================================================
# 5. CREATE ALLOCATION MAPS FOR K=40
# ============================================================================
print("\n" + "=" * 80)
print("### 5. CREATING ALLOCATION MAPS ###")
print("=" * 80)

# Load geographic data
firehouses_df = pd.read_csv(PROCESSED_DIR / 'firehouses_manhattan.csv')
precincts_gdf = gpd.read_file(PROCESSED_DIR / 'precincts_manhattan.geojson')
demand_df = pd.read_csv(PROCESSED_DIR / 'demand_lambda_precinct.csv')
demand_df['precinct'] = demand_df['precinct'].astype(str)

# Merge demand with precincts
precincts_gdf['Precinct'] = precincts_gdf['Precinct'].astype(str)
precincts_gdf = precincts_gdf.merge(
    demand_df[['precinct', 'crash_rate_per_hour']], 
    left_on='Precinct', right_on='precinct', how='left'
)
precincts_gdf['lambda_per_day'] = precincts_gdf['crash_rate_per_hour'] * 24

K_FOR_MAPS = 40

for policy_id in ['P0', 'P1', 'P2']:
    print(f"Creating map for {policy_id}...")
    
    # Get allocation for this policy at K=40
    K40_allocs = allocation_tables[K_FOR_MAPS]
    policy_alloc = None
    for alloc_df in K40_allocs:
        if (alloc_df['policy'] == policy_id).any():
            policy_alloc = alloc_df[alloc_df['policy'] == policy_id].set_index('firehouse')['units']
            break
    
    if policy_alloc is None:
        continue
    
    # Merge with firehouse coordinates
    fh_plot = firehouses_df.copy()
    fh_plot['FacilityName'] = fh_plot['FacilityName'].str.strip()
    fh_plot = fh_plot.set_index('FacilityName')
    fh_plot['units'] = policy_alloc.reindex(fh_plot.index, fill_value=0)
    
    # Create map
    fig, ax = plt.subplots(figsize=(12, 14))
    
    # Plot precincts with demand heatmap
    precincts_gdf.plot(
        column='lambda_per_day',
        ax=ax,
        cmap='YlOrRd',
        alpha=0.6,
        edgecolor='black',
        linewidth=0.5,
        legend=True,
        legend_kwds={'label': 'Demand (crashes/day)', 'shrink': 0.6}
    )
    
    # Plot firehouses with graduated symbols
    fh_active = fh_plot[fh_plot['units'] > 0]
    fh_inactive = fh_plot[fh_plot['units'] == 0]
    
    # Active firehouses (size proportional to units)
    if len(fh_active) > 0:
        sizes = fh_active['units'] * 100  # Scale for visibility
        ax.scatter(
            fh_active['Longitude'], fh_active['Latitude'],
            s=sizes, c='blue', alpha=0.7, edgecolors='black', linewidth=1.5,
            label='Active Firehouse', zorder=5
        )
        
        # Annotate with unit count
        for idx, row in fh_active.iterrows():
            ax.annotate(
                f"{int(row['units'])}",
                (row['Longitude'], row['Latitude']),
                fontsize=9, fontweight='bold', ha='center', va='center',
                color='white', zorder=6
            )
    
    # Inactive firehouses
    if len(fh_inactive) > 0:
        ax.scatter(
            fh_inactive['Longitude'], fh_inactive['Latitude'],
            s=50, c='gray', alpha=0.3, edgecolors='black', linewidth=0.5,
            label='Inactive Firehouse', zorder=4, marker='x'
        )
    
    # Formatting
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(f'{POLICIES[policy_id]["name"]} Allocation (K={K_FOR_MAPS})', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig(MAPS_DIR / f'map_allocation_{policy_id}_K{K_FOR_MAPS}.png', 
                dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: map_allocation_{policy_id}_K{K_FOR_MAPS}.png")

# ============================================================================
# 6. KEY FINDINGS SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("### 6. KEY FINDINGS ###")
print("=" * 80)

# Find best policy for each K
best_policies = []
for K in K_VALUES:
    K_data = results_df[results_df['K'] == K].copy()
    
    # Best by response time (minimum)
    best_rt = K_data.loc[K_data['response_time'].idxmin()]
    
    # Best by coverage (maximum)
    best_cov = K_data.loc[K_data['pct_demand_covered'].idxmax()]
    
    print(f"\nK = {K}:")
    print(f"  Best Response Time: {best_rt['policy_id']} ({best_rt['policy_name']}) - {best_rt['response_time']:.2f} min")
    print(f"  Best Coverage: {best_cov['policy_id']} ({best_cov['policy_name']}) - {best_cov['pct_demand_covered']:.1f}%")
    
    # Compare P0 vs P2
    P0_row = K_data[K_data['policy_id'] == 'P0'].iloc[0]
    P2_row = K_data[K_data['policy_id'] == 'P2'].iloc[0]
    
    rt_improvement = (P0_row['response_time'] - P2_row['response_time']) / P0_row['response_time'] * 100
    cov_improvement = P2_row['pct_demand_covered'] - P0_row['pct_demand_covered']
    
    print(f"  P2 vs P0: {rt_improvement:.1f}% faster response, {cov_improvement:.1f}% more coverage")

# Diminishing returns analysis
print("\n--- Diminishing Returns ---")
for policy_id in ['P0', 'P2']:
    policy_data = results_df[results_df['policy_id'] == policy_id].sort_values('K')
    print(f"\n{POLICIES[policy_id]['name']}:")
    for i in range(1, len(policy_data)):
        prev = policy_data.iloc[i-1]
        curr = policy_data.iloc[i]
        delta_K = curr['K'] - prev['K']
        delta_rt = prev['response_time'] - curr['response_time']
        delta_cov = curr['pct_demand_covered'] - prev['pct_demand_covered']
        print(f"  {int(prev['K'])}→{int(curr['K'])}: "
              f"ΔRT = {delta_rt:.2f} min ({delta_rt/delta_K:.3f} min/unit), "
              f"ΔCov = {delta_cov:.1f}%")

# Save findings summary
findings = {
    'best_overall_response': results_df.loc[results_df['response_time'].idxmin()].to_dict(),
    'best_overall_coverage': results_df.loc[results_df['pct_demand_covered'].idxmax()].to_dict(),
    'policy_rankings_K40': results_df[results_df['K'] == 40].sort_values('response_time')[
        ['policy_id', 'policy_name', 'response_time', 'pct_demand_covered']
    ].to_dict('records')
}

with open(RESULTS_DIR / 'findings_summary.json', 'w') as f:
    json.dump(findings, f, indent=2, default=str)
print(f"\nSaved: findings_summary.json")

print("\n" + "=" * 80)
print("OPTIMIZATION COMPARISON COMPLETE")
print("=" * 80)
print(f"\nOutputs saved to:")
print(f"  - {RESULTS_DIR}/")
print(f"  - {MAPS_DIR}/")
print(f"  - {FIGURES_DIR}/")
