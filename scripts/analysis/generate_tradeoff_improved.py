#!/usr/bin/env python3
"""
Generate an improved Response Time vs Coverage Trade-off visualization.

Fixes overlapping labels from the original fig_tradeoff_curve.png by:
  - Using different marker shapes per policy
  - Adding adjustText-based label repulsion (or manual offsets)
  - Drawing connecting lines for same policy across fleet sizes
  - Adding an annotation table for exact values
  - Improved legend with full policy names
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CAPACITY = 2  # v2 baseline uses capacity=2 (DEC-010)
RESULTS_DIR = BASE_DIR / 'results' / 'baseline' / 'simulation'
FIGURES_DIR = BASE_DIR / 'results' / 'figures'

# Load V2 baseline data and build tradeoff table
_raw = pd.read_csv(RESULTS_DIR / 'all_results_raw.csv')
# Aggregate per (policy, K): mean response_time and mean coverage_8min
_agg = _raw.groupby(['policy', 'K']).agg(
    response_time=('mean_response_time', 'mean'),
    pct_demand_covered=('coverage_8min', lambda x: x.mean() * 100),
).reset_index()
_agg.rename(columns={'policy': 'policy_id'}, inplace=True)
results_df = _agg

print("Data loaded:")
print(results_df[['K', 'policy_id', 'response_time', 'pct_demand_covered']].to_string(index=False))

# ============================================================================
# Policy display configuration
# ============================================================================
POLICY_INFO = {
    'P0':  {'name': 'P0: Spatially-Stratified Baseline',  'marker': 's', 'zorder': 5},
    'P1':  {'name': 'P1: Demand-Proportional',             'marker': '^', 'zorder': 6},
    'P2':  {'name': 'P2: Demand-Weighted Opt.',            'marker': 'o', 'zorder': 7},
}

K_COLORS = {
    10: '#9467bd', 15: '#8c564b', 20: '#1f77b4', 25: '#17becf',
    30: '#ff7f0e', 35: '#bcbd22', 40: '#2ca02c', 45: '#e377c2', 48: '#d62728',
}

# ============================================================================
# Figure 1: Improved scatter with jitter and smart annotations
# ============================================================================
fig, (ax_main, ax_table) = plt.subplots(
    1, 2, figsize=(16, 8),
    gridspec_kw={'width_ratios': [3, 1.2]},
)

# -- Main scatter plot --
# Group overlapping points to apply jitter
coords = results_df[['response_time', 'pct_demand_covered']].round(2)
results_df['rt_round'] = coords['response_time']
results_df['cov_round'] = coords['pct_demand_covered']

# Detect clusters of overlapping points
from collections import defaultdict
clusters = defaultdict(list)
for idx, row in results_df.iterrows():
    key = (row['rt_round'], row['cov_round'])
    clusters[key].append(idx)

# Calculate jitter offsets for overlapping points
jitter_x = np.zeros(len(results_df))
jitter_y = np.zeros(len(results_df))

for key, indices in clusters.items():
    n = len(indices)
    if n > 1:
        # Arrange in a circle around the true point
        radius_x = 0.15 * max(1, n / 4)
        radius_y = 0.4 * max(1, n / 4)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        for i, idx in enumerate(indices):
            jitter_x[idx] = radius_x * np.cos(angles[i])
            jitter_y[idx] = radius_y * np.sin(angles[i])

results_df['rt_jittered'] = results_df['response_time'] + jitter_x
results_df['cov_jittered'] = results_df['pct_demand_covered'] + jitter_y

# Plot each point
for _, row in results_df.iterrows():
    pid = row['policy_id']
    K = row['K']
    info = POLICY_INFO.get(pid, {'marker': 'o', 'zorder': 5})
    ax_main.scatter(
        row['rt_jittered'], row['cov_jittered'],
        s=180, alpha=0.85,
        color=K_COLORS[K],
        marker=info['marker'],
        edgecolors='black', linewidths=0.5,
        zorder=info['zorder'],
    )

# Draw connecting lines for same policy across K values
for pid in results_df['policy_id'].unique():
    subset = results_df[results_df['policy_id'] == pid].sort_values('K')
    if len(subset) > 1:
        ax_main.plot(
            subset['rt_jittered'], subset['cov_jittered'],
            '--', alpha=0.3, color='gray', linewidth=1, zorder=1,
        )

# Annotate points - only annotate non-overlapping or use smart offsets
annotated = set()
for _, row in results_df.iterrows():
    pid = row['policy_id']
    K = row['K']
    key = (row['rt_round'], row['cov_round'])
    n_overlap = len(clusters[key])

    # For highly clustered points (upper-left corner), only label once per policy
    if n_overlap > 3:
        label_key = (pid, round(row['rt_round'], 1))
        if label_key in annotated:
            continue
        annotated.add(label_key)

    # Choose offset direction based on position
    if row['response_time'] > 10:
        ha, va, dx, dy = 'right', 'top', -0.3, -0.5
    elif row['cov_jittered'] < 95:
        ha, va, dx, dy = 'left', 'top', 0.3, -0.5
    else:
        ha, va, dx, dy = 'left', 'bottom', 0.15, 0.3

    label = f"{pid}\nK={K}"
    ax_main.annotate(
        label,
        (row['rt_jittered'], row['cov_jittered']),
        xytext=(row['rt_jittered'] + dx, row['cov_jittered'] + dy),
        fontsize=7, ha=ha, va=va,
        arrowprops=dict(arrowstyle='-', color='gray', alpha=0.4, lw=0.5),
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='none'),
        zorder=10,
    )

# Legends
# Fleet size legend (colors)
K_handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=c, markersize=10,
                     label=f'K={k}') for k, c in K_COLORS.items()]
legend1 = ax_main.legend(handles=K_handles, title='Fleet Size', loc='center right',
                          fontsize=9, title_fontsize=10)
ax_main.add_artist(legend1)

# Policy legend (marker shapes)
P_handles = [Line2D([0], [0], marker=info['marker'], color='w', markerfacecolor='gray',
                     markersize=10, label=info['name']) for info in POLICY_INFO.values()]
legend2 = ax_main.legend(handles=P_handles, title='Policy', loc='lower left',
                          fontsize=8, title_fontsize=9)

ax_main.set_xlabel('Expected Response Time (minutes)', fontsize=12)
ax_main.set_ylabel('% Demand Covered (<=8 min, NFPA)', fontsize=12)
ax_main.set_title(f'Response Time vs Coverage Trade-off (cap={CAPACITY})', fontsize=14, fontweight='bold')
ax_main.grid(True, alpha=0.3)

# Add threshold reference lines
ax_main.axvline(x=6.0, color='orange', linestyle=':', alpha=0.5, label='6-min NYC target')
ax_main.axvline(x=8.0, color='red', linestyle=':', alpha=0.4, label='8-min NFPA target')

# -- Data table panel --
ax_table.axis('off')

# Create summary table
table_data = []
for K in sorted(results_df['K'].unique()):
    for pid in ['P0', 'P1', 'P2']:
        row = results_df[(results_df['K'] == K) & (results_df['policy_id'] == pid)]
        if len(row) > 0:
            r = row.iloc[0]
            table_data.append([
                f"K={K}", pid,
                f"{r['response_time']:.2f}",
                f"{r['pct_demand_covered']:.1f}%",
            ])

table = ax_table.table(
    cellText=table_data,
    colLabels=['Fleet', 'Policy', 'RT (min)', 'Coverage'],
    loc='center',
    cellLoc='center',
)
table.auto_set_font_size(False)
table.set_fontsize(7.5)
table.scale(1.0, 1.15)

# Color header cells
for j in range(4):
    table[0, j].set_facecolor('#4472C4')
    table[0, j].set_text_props(color='white', fontweight='bold')

# Alternate row shading
for i in range(1, len(table_data) + 1):
    for j in range(4):
        if (i - 1) // 5 % 2 == 1:
            table[i, j].set_facecolor('#f0f0f0')

ax_table.set_title(f'Exact Values (cap={CAPACITY})', fontsize=11, fontweight='bold', pad=10)

plt.tight_layout()
out_path = FIGURES_DIR / 'response_time_coverage_tradeoff_improved.png'
plt.savefig(out_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"\nSaved improved plot: {out_path}")


# ============================================================================
# Figure 2: Zoomed-in view of the clustered upper-left corner
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 7))

# Filter to the clustered region (RT < 5, Coverage > 98)
clustered = results_df[
    (results_df['response_time'] < 5) & (results_df['pct_demand_covered'] >= 98)
].copy()

print(f"\nClustered region: {len(clustered)} points")

# Plot with larger jitter for visibility
np.random.seed(42)
for _, row in clustered.iterrows():
    pid = row['policy_id']
    K = row['K']
    info = POLICY_INFO.get(pid, {'marker': 'o', 'zorder': 5})
    ax.scatter(
        row['rt_jittered'], row['cov_jittered'],
        s=220, alpha=0.85,
        color=K_COLORS[K],
        marker=info['marker'],
        edgecolors='black', linewidths=0.7,
        zorder=info['zorder'],
    )
    # Label every point in zoomed view
    ax.annotate(
        f"{pid} (K={K})",
        (row['rt_jittered'], row['cov_jittered']),
        fontsize=8.5, ha='left', va='bottom',
        xytext=(5, 5), textcoords='offset points',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='gray', linewidth=0.5),
        zorder=10,
    )

# Legends
K_handles = [Line2D([0], [0], marker='o', color='w', markerfacecolor=c, markersize=10,
                     label=f'K={k}') for k, c in K_COLORS.items()]
legend1 = ax.legend(handles=K_handles, title='Fleet Size', loc='upper right',
                     fontsize=9, title_fontsize=10)
ax.add_artist(legend1)

P_handles = [Line2D([0], [0], marker=info['marker'], color='w', markerfacecolor='gray',
                     markersize=10, label=info['name']) for info in POLICY_INFO.values()]
ax.legend(handles=P_handles, title='Policy', loc='lower left', fontsize=8, title_fontsize=9)

ax.set_xlabel('Expected Response Time (minutes)', fontsize=12)
ax.set_ylabel('% Demand Covered (<=8 min, NFPA)', fontsize=12)
ax.set_title(f'Trade-off Detail: High-Performance Region (RT < 5 min, cap={CAPACITY})', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
zoom_path = FIGURES_DIR / 'response_time_coverage_tradeoff_zoomed.png'
plt.savefig(zoom_path, dpi=200, bbox_inches='tight')
plt.close()
print(f"Saved zoomed plot: {zoom_path}")

print("\nDone!")
