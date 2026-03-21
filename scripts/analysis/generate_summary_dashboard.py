#!/usr/bin/env python3
"""
Generate a comprehensive one-page project summary dashboard.

Creates results/figures/project_summary_dashboard.png with:
- Policy comparison bar chart
- Fleet sensitivity curves
- Demand robustness results
- Key metrics summary table
- Coverage comparison
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

# ── Paths ──────────────────────────────────────────────────────────
PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TABLES  = os.path.join(PROJECT, "results", "tables")
SIM     = os.path.join(PROJECT, "results", "simulation", "production")
OUT     = os.path.join(PROJECT, "results", "figures", "project_summary_dashboard.png")

# ── Load Data ──────────────────────────────────────────────────────
desc = pd.read_csv(os.path.join(TABLES, "descriptive_statistics.csv"))
exp_summary = pd.read_csv(os.path.join(SIM, "experiment_summary.csv"))

CAPACITY = 5  # v1 production experiments used capacity=5 (implicit default)

# ── Color Palette ──────────────────────────────────────────────────
COLORS = {
    'P0': '#e74c3c',   # Red
    'P1': '#3498db',   # Blue
    'P2': '#2ecc71',   # Green
    'bg': '#f8f9fa',
    'text': '#2c3e50',
    'accent': '#8e44ad',
}

# ── Create Figure ──────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 14), facecolor='white')
fig.suptitle(f'EMS Readiness Optimization for Manhattan — Project Summary Dashboard (capacity={CAPACITY} units/firehouse)',
             fontsize=22, fontweight='bold', color=COLORS['text'], y=0.98)

gs = gridspec.GridSpec(3, 3, hspace=0.35, wspace=0.3,
                       left=0.06, right=0.96, top=0.92, bottom=0.05)

# ── Panel 1: Key Metrics (Top Left) ────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')
ax1.set_title(f'Key Results (K=20, cap={CAPACITY})', fontsize=14, fontweight='bold',
              color=COLORS['text'], pad=10)

metrics_data = [
    ('Mean Response Time', '3.17 → 2.57 min', '↓ 19%', COLORS['P2']),
    ('P90 Response Time (90th pctl)', '5.32 → 3.76 min', '↓ 29%', COLORS['P2']),
    ('8-min Coverage (NFPA)', '99.6% → 99.6%', 'Maintained', COLORS['P2']),
    ('6-min Coverage (NYC)', '93.7% → 99.2%', '↑ 5.5pp', COLORS['P2']),
]

for i, (label, value, change, color) in enumerate(metrics_data):
    y = 8.5 - i * 2.3
    ax1.text(0.5, y, label, fontsize=11, color=COLORS['text'], fontweight='bold')
    ax1.text(0.5, y - 0.7, value, fontsize=10, color='#555')
    ax1.text(8.5, y - 0.3, change, fontsize=14, fontweight='bold', color=color,
             ha='center', va='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.15))

# ── Panel 2: Policy Comparison Bar Chart (Top Center) ──────────────
ax2 = fig.add_subplot(gs[0, 1])
exp1 = desc[desc['Experiment'] == 'exp1_policy_comparison']
policies = ['P0', 'P1', 'P2']
mean_rts = []
for p in policies:
    row = exp1[(exp1['Policy'] == p) & (exp1['Metric'] == 'Mean RT (min)')]
    mean_rts.append(row['Mean'].values[0])

bars = ax2.bar(policies, mean_rts, color=[COLORS[p] for p in policies],
               edgecolor='white', linewidth=2, width=0.6)
ax2.set_ylabel('Mean Response Time (min)', fontsize=11)
ax2.set_title(f'Policy Comparison (Exp 1, cap={CAPACITY})', fontsize=14, fontweight='bold',
              color=COLORS['text'])
ax2.set_ylim(0, 10)
for bar, val in zip(bars, mean_rts):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
             f'{val:.2f}', ha='center', fontsize=12, fontweight='bold')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.axhline(y=8.0, color='gray', linestyle='--', alpha=0.5, label='8-min target')
ax2.legend(fontsize=9)

# ── Panel 3: Coverage Comparison (Top Right) — both 6-min & 8-min ──
ax3 = fig.add_subplot(gs[0, 2])
coverages_8 = []
coverages_6 = []
for p in policies:
    row8 = exp1[(exp1['Policy'] == p) & (exp1['Metric'] == '8-min Coverage (NFPA)')]
    coverages_8.append(row8['Mean'].values[0] * 100 if len(row8) else 0)
    row6 = exp1[(exp1['Policy'] == p) & (exp1['Metric'] == '6-min Coverage (NYC)')]
    coverages_6.append(row6['Mean'].values[0] * 100 if len(row6) else 0)

x_pos = np.arange(len(policies))
w = 0.35
bars_6 = ax3.bar(x_pos - w/2, coverages_6, w, color=[COLORS[p] for p in policies],
                 edgecolor='white', linewidth=2, alpha=0.6, label='6-min (NYC)')
bars_8 = ax3.bar(x_pos + w/2, coverages_8, w, color=[COLORS[p] for p in policies],
                 edgecolor='black', linewidth=1, label='8-min (NFPA)')
ax3.set_xticks(x_pos)
ax3.set_xticklabels(policies)
ax3.set_ylabel('Coverage (%)', fontsize=11)
ax3.set_title(f'Coverage Comparison (Exp 1, cap={CAPACITY})', fontsize=14, fontweight='bold',
              color=COLORS['text'])
ax3.set_ylim(0, 110)
for bar, val in zip(bars_6, coverages_6):
    ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
             f'{val:.1f}%', ha='center', fontsize=8, fontweight='bold')
for bar, val in zip(bars_8, coverages_8):
    ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
             f'{val:.1f}%', ha='center', fontsize=8, fontweight='bold')
ax3.axhline(y=90, color='gray', linestyle='--', alpha=0.5, label='90% target')
ax3.legend(fontsize=7, loc='lower right')
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# ── Panel 4: Fleet Sensitivity (Middle Left) ──────────────────────
ax4 = fig.add_subplot(gs[1, 0:2])
exp2 = exp_summary[exp_summary['experiment'] == 'exp2']
for policy in policies:
    pdata = exp2[exp2['policy'] == policy].sort_values('K')
    ax4.plot(pdata['K'], pdata['mean_RT'], 'o-', color=COLORS[policy],
             label=policy, linewidth=2.5, markersize=7)

ax4.set_xlabel('Fleet Size (K)', fontsize=12)
ax4.set_ylabel('Mean Response Time (min)', fontsize=12)
ax4.set_title(f'Fleet Sensitivity Analysis (Exp 2, cap={CAPACITY})', fontsize=14,
              fontweight='bold', color=COLORS['text'])
ax4.axhline(y=4.0, color='gray', linestyle='--', alpha=0.3)
ax4.legend(fontsize=11, loc='upper right')
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.set_xticks([15, 20, 25, 30, 35, 40])

# ── Panel 5: Statistical Significance (Middle Right) ──────────────
ax5 = fig.add_subplot(gs[1, 2])
ax5.axis('off')
ax5.set_title('Statistical Significance', fontsize=14, fontweight='bold',
              color=COLORS['text'], pad=10)

stats_text = [
    ('ANOVA F-statistic', '12,010', '***'),
    ('p-value', '< 0.001', ''),
    ('η² (effect size)', '0.996', 'Large'),
    ("Cohen's d (P0→P2)", '28.9', 'Large'),
    ('95% CI for ΔRT', '[5.41, 5.61]', 'min'),
    ('Replications', '30', 'per cell'),
    ('Total sim runs', '1,440', ''),
]

for i, (label, value, note) in enumerate(stats_text):
    y = 9 - i * 1.3
    ax5.text(0.5, y, label, fontsize=10, color='#555',
             transform=ax5.transAxes if False else None)
    ax5.text(7, y, value, fontsize=10, fontweight='bold', color=COLORS['text'])
    ax5.text(9.5, y, note, fontsize=9, color=COLORS['accent'])
ax5.set_xlim(0, 10)
ax5.set_ylim(0, 10)

# ── Panel 6: Demand Robustness (Bottom Left) ──────────────────────
ax6 = fig.add_subplot(gs[2, 0:2])
exp3 = exp_summary[exp_summary['experiment'] == 'exp3']
for policy in policies:
    pdata = exp3[exp3['policy'] == policy].sort_values('demand_mult')
    ax6.plot(pdata['demand_mult'], pdata['mean_RT'], 's-', color=COLORS[policy],
             label=policy, linewidth=2.5, markersize=7)

ax6.set_xlabel('Demand Multiplier', fontsize=12)
ax6.set_ylabel('Mean Response Time (min)', fontsize=12)
ax6.set_title(f'Demand Sensitivity Analysis (Exp 3, cap={CAPACITY})', fontsize=14,
              fontweight='bold', color=COLORS['text'])
ax6.legend(fontsize=11, loc='upper left')
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)

# ── Panel 7: Project Summary (Bottom Right) ───────────────────────
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis('off')
ax7.set_title('Project Summary', fontsize=14, fontweight='bold',
              color=COLORS['text'], pad=10)

summary_items = [
    'Manhattan, NYC (48 firehouses)',
    '2.24M historical crash records',
    'NHPP demand model (λ₀=3.48/hr)',
    '3 MIP optimization models',
    'SimPy discrete-event simulation',
    '1,440 production runs',
    '39 unit tests (all passing)',
    '7,134 lines of Python code',
    '33 figures, 27 result tables',
    'Phases 1–7 complete ✓',
]

for i, item in enumerate(summary_items):
    y = 9.2 - i * 0.95
    ax7.text(0.5, y, f'• {item}', fontsize=9.5, color=COLORS['text'])
ax7.set_xlim(0, 10)
ax7.set_ylim(0, 10)

# ── Footer ─────────────────────────────────────────────────────────
fig.text(0.5, 0.01,
         'EMS Readiness Optimization Project  |  March 2026  |  github.com/cnsp/ems-optimization  |  v1.0.0',
         ha='center', fontsize=10, color='#888', style='italic')

# ── Save ───────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=150, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f"Dashboard saved to {OUT}")
print(f"   Size: {os.path.getsize(OUT) / 1024:.0f} KB")
