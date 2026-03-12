#!/usr/bin/env python3
"""
EMS Optimization Project - Demand Modeling
Comprehensive input modeling for crash demand arrivals
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')

# Set plot style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

# Paths
BASE_DIR = Path('/home/ubuntu/ems-optimization')
PROCESSED_DIR = BASE_DIR / 'data/processed'
RESULTS_DIR = BASE_DIR / 'results/figures'

print("=" * 80)
print("EMS OPTIMIZATION - DEMAND MODELING")
print("=" * 80)

# ============================================================================
# 1. DATA PREPARATION
# ============================================================================
print("\n### 1. DATA PREPARATION ###\n")

# Load crash data
df = pd.read_parquet(PROCESSED_DIR / 'crashes_manhattan.parquet')
print(f"Loaded {len(df):,} Manhattan crash records")

# Parse datetime
df['crash_datetime'] = pd.to_datetime(df['crash_datetime'])
df['date'] = df['crash_datetime'].dt.date
df['hour'] = df['crash_datetime'].dt.hour
df['dow'] = df['crash_datetime'].dt.dayofweek  # 0=Monday, 6=Sunday
df['dow_name'] = df['crash_datetime'].dt.day_name()
df['month'] = df['crash_datetime'].dt.month
df['year'] = df['crash_datetime'].dt.year
df['week'] = df['crash_datetime'].dt.isocalendar().week

# Date range
date_min = df['crash_datetime'].min()
date_max = df['crash_datetime'].max()
total_hours = (date_max - date_min).total_seconds() / 3600
total_days = total_hours / 24

print(f"Date range: {date_min} to {date_max}")
print(f"Total duration: {total_days:.1f} days ({total_hours:.0f} hours)")
print(f"Average crashes per day: {len(df) / total_days:.2f}")
print(f"Average crashes per hour: {len(df) / total_hours:.4f}")

# Aggregate by time periods
hourly_counts = df.groupby([df['crash_datetime'].dt.floor('H')]).size()
daily_counts = df.groupby('date').size()

print(f"\nHourly counts: mean={hourly_counts.mean():.2f}, std={hourly_counts.std():.2f}")
print(f"Daily counts: mean={daily_counts.mean():.2f}, std={daily_counts.std():.2f}")

# ============================================================================
# 2. SPATIAL JOIN WITH PRECINCTS
# ============================================================================
print("\n### 2. SPATIAL JOIN WITH PRECINCTS ###\n")

# Load precincts
precincts = gpd.read_file(PROCESSED_DIR / 'precincts_manhattan.geojson')
print(f"Loaded {len(precincts)} Manhattan precincts")

# Create geometry for crashes
geometry = [Point(xy) for xy in zip(df['LONGITUDE'], df['LATITUDE'])]
crashes_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')

# Spatial join
crashes_with_precinct = gpd.sjoin(crashes_gdf, precincts[['Precinct', 'geometry']], 
                                   how='left', predicate='within')
crashes_with_precinct = crashes_with_precinct.rename(columns={'Precinct': 'precinct'})

# Count crashes per precinct
precinct_counts = crashes_with_precinct.groupby('precinct').size().sort_values(ascending=False)
print(f"Crashes assigned to precincts: {crashes_with_precinct['precinct'].notna().sum():,}")
print(f"Top 5 precincts by crash count:")
print(precinct_counts.head().to_string())

# ============================================================================
# 3. HOMOGENEOUS POISSON MODEL
# ============================================================================
print("\n" + "=" * 80)
print("### 3. HOMOGENEOUS POISSON MODEL ###")
print("=" * 80)

# Estimate overall arrival rate (crashes per hour)
lambda_overall = len(df) / total_hours
print(f"\nOverall arrival rate (λ): {lambda_overall:.4f} crashes/hour")
print(f"  = {lambda_overall * 24:.2f} crashes/day")

# Test Poisson assumption using chi-square goodness-of-fit on hourly data
print("\n--- Chi-Square Goodness-of-Fit Test (Hourly Counts) ---")

# Get observed frequency distribution
observed_freq = hourly_counts.value_counts().sort_index()
max_count = int(observed_freq.index.max())

# Expected frequencies under Poisson(lambda_overall)
n_hours = len(hourly_counts)
expected_counts = []
observed_counts = []
bins = list(range(0, min(max_count, 15) + 1)) + [float('inf')]

for i in range(len(bins) - 1):
    if bins[i+1] == float('inf'):
        # Last bin: k >= bins[i]
        expected_prob = 1 - stats.poisson.cdf(bins[i] - 1, lambda_overall)
        obs_count = observed_freq[observed_freq.index >= bins[i]].sum()
    else:
        expected_prob = stats.poisson.pmf(bins[i], lambda_overall)
        obs_count = observed_freq.get(bins[i], 0)
    
    expected_counts.append(expected_prob * n_hours)
    observed_counts.append(obs_count)

# Combine bins with expected < 5
combined_obs = []
combined_exp = []
temp_obs = 0
temp_exp = 0

for obs, exp in zip(observed_counts, expected_counts):
    temp_obs += obs
    temp_exp += exp
    if temp_exp >= 5:
        combined_obs.append(temp_obs)
        combined_exp.append(temp_exp)
        temp_obs = 0
        temp_exp = 0

if temp_exp > 0:
    combined_obs[-1] += temp_obs
    combined_exp[-1] += temp_exp

# Chi-square test
chi2_stat = sum((o - e)**2 / e for o, e in zip(combined_obs, combined_exp))
dof = len(combined_obs) - 1 - 1  # -1 for estimated lambda
p_value = 1 - stats.chi2.cdf(chi2_stat, dof)

print(f"Chi-square statistic: {chi2_stat:.2f}")
print(f"Degrees of freedom: {dof}")
print(f"P-value: {p_value:.4e}")

if p_value < 0.05:
    print("Result: REJECT homogeneous Poisson assumption (p < 0.05)")
    print("        -> Non-homogeneous Poisson (NHPP) is more appropriate")
else:
    print("Result: Cannot reject homogeneous Poisson assumption")

# Dispersion test (variance/mean ratio)
dispersion = hourly_counts.var() / hourly_counts.mean()
print(f"\nDispersion (Var/Mean): {dispersion:.4f}")
if dispersion > 1.5:
    print("  -> Overdispersion detected; time-varying rates likely")

# ============================================================================
# 4. NON-HOMOGENEOUS POISSON (NHPP) MODEL
# ============================================================================
print("\n" + "=" * 80)
print("### 4. NON-HOMOGENEOUS POISSON PROCESS (NHPP) MODEL ###")
print("=" * 80)

# 4a. Estimate hourly arrival rates
print("\n--- Hourly Rates (24-hour pattern) ---")
hourly_crash_counts = df.groupby('hour').size()

# Count number of each hour in the dataset
hour_totals = df.groupby('hour')['crash_datetime'].apply(
    lambda x: (x.max() - x.min()).total_seconds() / 3600 / len(x.unique()) if len(x) > 0 else 1
)

# Better approach: count distinct hours in dataset
date_hour_counts = df.groupby(['date', 'hour']).size().reset_index(name='crashes')
hours_per_bucket = date_hour_counts.groupby('hour').size()

lambda_hourly = hourly_crash_counts / hours_per_bucket
lambda_hourly_normalized = lambda_hourly / lambda_hourly.mean()

print("\nHourly arrival rates (λ_h):")
hourly_df = pd.DataFrame({
    'hour': range(24),
    'crashes': hourly_crash_counts.values,
    'lambda_per_hour': lambda_hourly.values,
    'factor': lambda_hourly_normalized.values
})
print(hourly_df.to_string(index=False))

# 4b. Day-of-week multipliers
print("\n--- Day-of-Week Factors ---")
dow_crash_counts = df.groupby('dow').size()
dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Count days per dow in dataset
unique_dates = df['date'].unique()
dates_df = pd.DataFrame({'date': unique_dates})
dates_df['dow'] = pd.to_datetime(dates_df['date']).dt.dayofweek
days_per_dow = dates_df.groupby('dow').size()

lambda_dow = dow_crash_counts / days_per_dow
lambda_dow_normalized = lambda_dow / lambda_dow.mean()

print("\nDay-of-week factors:")
dow_df = pd.DataFrame({
    'dow': range(7),
    'day_name': dow_names,
    'crashes': dow_crash_counts.values,
    'num_days': days_per_dow.values,
    'lambda_per_day': lambda_dow.values,
    'factor': lambda_dow_normalized.values
})
print(dow_df.to_string(index=False))

# 4c. Combined rate function
print("\n--- Combined NHPP Rate Function ---")
print("λ(t) = base_rate × hour_factor[h] × dow_factor[d]")
base_rate = lambda_overall
print(f"Base rate: {base_rate:.4f} crashes/hour")

# 4d. Validation with holdout data
print("\n--- Model Validation ---")

# Use last 20% of data as holdout
split_date = df['crash_datetime'].quantile(0.8)
train_df = df[df['crash_datetime'] < split_date]
test_df = df[df['crash_datetime'] >= split_date]

print(f"Training set: {len(train_df):,} crashes ({train_df['crash_datetime'].min().date()} to {train_df['crash_datetime'].max().date()})")
print(f"Test set: {len(test_df):,} crashes ({test_df['crash_datetime'].min().date()} to {test_df['crash_datetime'].max().date()})")

# Fit model on training data
train_hourly = train_df.groupby('hour').size()
train_date_hour = train_df.groupby(['date', 'hour']).size().reset_index(name='crashes')
train_hours_per_bucket = train_date_hour.groupby('hour').size()
train_lambda_hourly = train_hourly / train_hours_per_bucket

train_dow = train_df.groupby('dow').size()
train_dates = train_df['date'].unique()
train_dates_df = pd.DataFrame({'date': train_dates})
train_dates_df['dow'] = pd.to_datetime(train_dates_df['date']).dt.dayofweek
train_days_per_dow = train_dates_df.groupby('dow').size()
train_lambda_dow = train_dow / train_days_per_dow

# Normalize
train_lambda_hourly_norm = train_lambda_hourly / train_lambda_hourly.mean()
train_lambda_dow_norm = train_lambda_dow / train_lambda_dow.mean()
train_base = len(train_df) / ((train_df['crash_datetime'].max() - train_df['crash_datetime'].min()).total_seconds() / 3600)

# Predict on test set
test_df = test_df.copy()
test_df['predicted_rate'] = test_df.apply(
    lambda row: train_base * train_lambda_hourly_norm[row['hour']] * train_lambda_dow_norm[row['dow']], 
    axis=1
)

# Compare predicted vs actual by hour
test_hourly_actual = test_df.groupby('hour').size()
test_hourly_pred = test_df.groupby('hour')['predicted_rate'].sum() / len(test_df['date'].unique())

# Calculate RMSE
rmse = np.sqrt(((test_hourly_actual - test_hourly_pred) ** 2).mean())
mae = (test_hourly_actual - test_hourly_pred).abs().mean()
mape = ((test_hourly_actual - test_hourly_pred).abs() / test_hourly_actual * 100).mean()

print(f"\nModel Performance (Hourly Level):")
print(f"  RMSE: {rmse:.2f}")
print(f"  MAE: {mae:.2f}")
print(f"  MAPE: {mape:.1f}%")

# ============================================================================
# 5. SPATIAL DEMAND MODEL (BY PRECINCT)
# ============================================================================
print("\n" + "=" * 80)
print("### 5. SPATIAL DEMAND MODEL (BY PRECINCT) ###")
print("=" * 80)

# Calculate lambda by precinct
precinct_lambda = crashes_with_precinct.groupby('precinct').size() / total_hours

precinct_df = pd.DataFrame({
    'precinct': precinct_lambda.index,
    'crashes': precinct_counts.loc[precinct_lambda.index].values,
    'lambda_per_hour': precinct_lambda.values,
    'lambda_per_day': (precinct_lambda * 24).values,
    'pct_of_total': (precinct_lambda / precinct_lambda.sum() * 100).values
}).sort_values('lambda_per_hour', ascending=False)

print("\nPrecinct-level arrival rates:")
print(precinct_df.to_string(index=False))

# Identify high/low demand zones
q75 = precinct_df['lambda_per_hour'].quantile(0.75)
q25 = precinct_df['lambda_per_hour'].quantile(0.25)

high_demand = precinct_df[precinct_df['lambda_per_hour'] >= q75]['precinct'].tolist()
low_demand = precinct_df[precinct_df['lambda_per_hour'] <= q25]['precinct'].tolist()

print(f"\nHigh-demand precincts (>=75th percentile): {high_demand}")
print(f"Low-demand precincts (<=25th percentile): {low_demand}")

# ============================================================================
# 6. CBD vs NON-CBD COMPARISON
# ============================================================================
print("\n" + "=" * 80)
print("### 6. CBD vs NON-CBD COMPARISON ###")
print("=" * 80)

cbd_df = df[df['in_cbd'] == True].copy()
non_cbd_df = df[df['in_cbd'] == False].copy()

print(f"\nCBD crashes: {len(cbd_df):,} ({len(cbd_df)/len(df)*100:.1f}%)")
print(f"Non-CBD crashes: {len(non_cbd_df):,} ({len(non_cbd_df)/len(df)*100:.1f}%)")

# Overall rates
lambda_cbd = len(cbd_df) / total_hours
lambda_non_cbd = len(non_cbd_df) / total_hours

print(f"\nOverall arrival rates:")
print(f"  CBD: {lambda_cbd:.4f} crashes/hour ({lambda_cbd*24:.2f}/day)")
print(f"  Non-CBD: {lambda_non_cbd:.4f} crashes/hour ({lambda_non_cbd*24:.2f}/day)")

# Hourly patterns
cbd_hourly = cbd_df.groupby('hour').size()
non_cbd_hourly = non_cbd_df.groupby('hour').size()

cbd_hourly_norm = cbd_hourly / cbd_hourly.mean()
non_cbd_hourly_norm = non_cbd_hourly / non_cbd_hourly.mean()

# Day-of-week patterns
cbd_dow = cbd_df.groupby('dow').size()
non_cbd_dow = non_cbd_df.groupby('dow').size()

cbd_dow_norm = cbd_dow / cbd_dow.mean()
non_cbd_dow_norm = non_cbd_dow / non_cbd_dow.mean()

print("\nHourly pattern comparison (peak hours):")
cbd_peak_hour = cbd_hourly_norm.idxmax()
non_cbd_peak_hour = non_cbd_hourly_norm.idxmax()
print(f"  CBD peak hour: {cbd_peak_hour}:00 (factor: {cbd_hourly_norm[cbd_peak_hour]:.2f})")
print(f"  Non-CBD peak hour: {non_cbd_peak_hour}:00 (factor: {non_cbd_hourly_norm[non_cbd_peak_hour]:.2f})")

print("\nDay-of-week pattern comparison (peak day):")
cbd_peak_dow = cbd_dow_norm.idxmax()
non_cbd_peak_dow = non_cbd_dow_norm.idxmax()
print(f"  CBD peak day: {dow_names[cbd_peak_dow]} (factor: {cbd_dow_norm[cbd_peak_dow]:.2f})")
print(f"  Non-CBD peak day: {dow_names[non_cbd_peak_dow]} (factor: {non_cbd_dow_norm[non_cbd_peak_dow]:.2f})")

# ============================================================================
# 7. SAVE OUTPUT FILES
# ============================================================================
print("\n" + "=" * 80)
print("### 7. SAVING OUTPUT FILES ###")
print("=" * 80)

# Hourly rates
hourly_output = pd.DataFrame({
    'hour': range(24),
    'lambda_per_hour': lambda_hourly.values,
    'factor': lambda_hourly_normalized.values,
    'cbd_factor': cbd_hourly_norm.values,
    'non_cbd_factor': non_cbd_hourly_norm.values
})
hourly_output.to_csv(PROCESSED_DIR / 'demand_lambda_hourly.csv', index=False)
print(f"Saved: demand_lambda_hourly.csv")

# Day-of-week factors
dow_output = pd.DataFrame({
    'dow': range(7),
    'day_name': dow_names,
    'lambda_per_day': lambda_dow.values,
    'factor': lambda_dow_normalized.values,
    'cbd_factor': cbd_dow_norm.values,
    'non_cbd_factor': non_cbd_dow_norm.values
})
dow_output.to_csv(PROCESSED_DIR / 'demand_lambda_dow.csv', index=False)
print(f"Saved: demand_lambda_dow.csv")

# Precinct rates
precinct_df.to_csv(PROCESSED_DIR / 'demand_lambda_precinct.csv', index=False)
print(f"Saved: demand_lambda_precinct.csv")

# ============================================================================
# 8. DIAGNOSTIC PLOTS
# ============================================================================
print("\n### 8. CREATING DIAGNOSTIC PLOTS ###")

# Figure 1: Model Fit Diagnostics
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1a. Observed vs Fitted hourly distribution
ax = axes[0, 0]
x_vals = range(int(hourly_counts.min()), min(int(hourly_counts.max()), 20))
observed_hist = [hourly_counts.value_counts().get(x, 0) for x in x_vals]
expected_hist = [stats.poisson.pmf(x, lambda_overall) * n_hours for x in x_vals]
width = 0.35
ax.bar([x - width/2 for x in x_vals], observed_hist, width, label='Observed', alpha=0.7)
ax.bar([x + width/2 for x in x_vals], expected_hist, width, label='Expected (Poisson)', alpha=0.7)
ax.set_xlabel('Crashes per Hour')
ax.set_ylabel('Frequency')
ax.set_title('Homogeneous Poisson: Observed vs Expected')
ax.legend()

# 1b. Hourly rates with confidence interval
ax = axes[0, 1]
hours = range(24)
ax.bar(hours, lambda_hourly.values, color='steelblue', alpha=0.7)
ax.axhline(y=lambda_overall, color='red', linestyle='--', label=f'Overall rate: {lambda_overall:.3f}')
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Arrival Rate (crashes/hour)')
ax.set_title('Hourly Arrival Rates (NHPP)')
ax.set_xticks(hours)
ax.legend()

# 1c. Day-of-week factors
ax = axes[1, 0]
x_pos = range(7)
ax.bar(x_pos, lambda_dow_normalized.values, color='darkorange', alpha=0.7)
ax.axhline(y=1.0, color='red', linestyle='--', label='Baseline (1.0)')
ax.set_xlabel('Day of Week')
ax.set_ylabel('Factor (relative to mean)')
ax.set_title('Day-of-Week Multipliers')
ax.set_xticks(x_pos)
ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
ax.legend()

# 1d. Q-Q plot for inter-arrival times
ax = axes[1, 1]
# Sample inter-arrival times (using hourly data as proxy)
hourly_sorted = hourly_counts.sort_index()
theoretical_quantiles = stats.poisson.ppf(np.linspace(0.01, 0.99, 100), lambda_overall)
empirical_quantiles = np.percentile(hourly_counts.values, np.linspace(1, 99, 100))
ax.scatter(theoretical_quantiles, empirical_quantiles, alpha=0.5)
max_val = max(theoretical_quantiles.max(), empirical_quantiles.max())
ax.plot([0, max_val], [0, max_val], 'r--', label='Perfect fit')
ax.set_xlabel('Theoretical Quantiles (Poisson)')
ax.set_ylabel('Empirical Quantiles')
ax.set_title('Q-Q Plot: Hourly Crash Counts')
ax.legend()

plt.tight_layout()
plt.savefig(RESULTS_DIR / 'fig_demand_model_fit.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: fig_demand_model_fit.png")

# Figure 2: Hourly rates comparison (CBD vs Non-CBD)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 2a. Hourly patterns
ax = axes[0]
hours = range(24)
ax.plot(hours, cbd_hourly_norm.values, 'o-', label='CBD', linewidth=2, markersize=6)
ax.plot(hours, non_cbd_hourly_norm.values, 's-', label='Non-CBD', linewidth=2, markersize=6)
ax.plot(hours, lambda_hourly_normalized.values, '^--', label='Overall', linewidth=1.5, alpha=0.7)
ax.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Factor (relative to mean)')
ax.set_title('Hourly Demand Patterns: CBD vs Non-CBD')
ax.set_xticks(hours)
ax.legend()
ax.grid(True, alpha=0.3)

# 2b. Day-of-week patterns
ax = axes[1]
x_pos = range(7)
width = 0.25
ax.bar([x - width for x in x_pos], cbd_dow_norm.values, width, label='CBD', alpha=0.8)
ax.bar(x_pos, non_cbd_dow_norm.values, width, label='Non-CBD', alpha=0.8)
ax.bar([x + width for x in x_pos], lambda_dow_normalized.values, width, label='Overall', alpha=0.8)
ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5)
ax.set_xlabel('Day of Week')
ax.set_ylabel('Factor (relative to mean)')
ax.set_title('Day-of-Week Patterns: CBD vs Non-CBD')
ax.set_xticks(x_pos)
ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
ax.legend()

plt.tight_layout()
plt.savefig(RESULTS_DIR / 'fig_hourly_rates.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: fig_hourly_rates.png")

# Figure 3: Precinct-level demand
fig, ax = plt.subplots(figsize=(14, 6))
precinct_sorted = precinct_df.sort_values('lambda_per_day', ascending=True)
y_pos = range(len(precinct_sorted))
bars = ax.barh(y_pos, precinct_sorted['lambda_per_day'].values, color='steelblue', alpha=0.7)

# Color high/low demand precincts
for i, (_, row) in enumerate(precinct_sorted.iterrows()):
    if row['precinct'] in high_demand:
        bars[i].set_color('crimson')
    elif row['precinct'] in low_demand:
        bars[i].set_color('forestgreen')

ax.set_yticks(y_pos)
ax.set_yticklabels([f"Pct {int(p)}" for p in precinct_sorted['precinct'].values])
ax.set_xlabel('Crashes per Day')
ax.set_title('Precinct-Level Demand Rates (Red=High, Green=Low)')
ax.axvline(x=precinct_sorted['lambda_per_day'].median(), color='orange', linestyle='--', 
           label=f'Median: {precinct_sorted["lambda_per_day"].median():.1f}')
ax.legend()

plt.tight_layout()
plt.savefig(RESULTS_DIR / 'fig_precinct_demand.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved: fig_precinct_demand.png")

print("\n" + "=" * 80)
print("DEMAND MODELING COMPLETE")
print("=" * 80)

# Store key results for documentation
results_summary = {
    'total_crashes': len(df),
    'date_range': f"{date_min.date()} to {date_max.date()}",
    'total_hours': total_hours,
    'lambda_overall': lambda_overall,
    'lambda_overall_per_day': lambda_overall * 24,
    'chi2_stat': chi2_stat,
    'chi2_pvalue': p_value,
    'dispersion': dispersion,
    'validation_rmse': rmse,
    'validation_mape': mape,
    'cbd_pct': len(cbd_df) / len(df) * 100,
    'lambda_cbd': lambda_cbd,
    'lambda_non_cbd': lambda_non_cbd,
    'peak_hour': int(lambda_hourly.idxmax()),
    'peak_dow': dow_names[int(lambda_dow.idxmax())],
    'high_demand_precincts': high_demand,
    'low_demand_precincts': low_demand
}

# Save summary
import json
with open(PROCESSED_DIR / 'demand_model_summary.json', 'w') as f:
    json.dump(results_summary, f, indent=2, default=str)
print(f"Saved: demand_model_summary.json")
