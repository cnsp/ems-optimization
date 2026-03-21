#!/usr/bin/env python3
"""Seasonal Pattern Analysis for EMS Optimization Study.

Analyzes monthly/seasonal variation in Manhattan crash demand to:
  1. Quantify seasonal amplitude
  2. Test for statistical significance of seasonal effects
  3. Justify use of annual average rate in NHPP model
  4. Generate seasonal visualizations

Generates:
  - results/figures/seasonal_patterns.png
  - results/figures/seasonal_decomposition.png
  - results/figures/seasonal_heatmap.png
  - results/tables/seasonal_analysis.csv

Usage:
    python scripts/analysis/analyze_seasonal_patterns.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 300, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 12,
})

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SEASON_COLORS = {
    "Winter": "#3498db", "Spring": "#2ecc71",
    "Summer": "#e74c3c", "Fall": "#f39c12",
}


def load_crash_data() -> pd.DataFrame:
    """Load and parse Manhattan crash data."""
    df = pd.read_csv(
        PROJECT_ROOT / "data" / "processed" / "crashes_manhattan.csv",
        usecols=["CRASH DATE", "CRASH TIME", "in_cbd"],
        parse_dates=["CRASH DATE"],
    )
    df["month"] = df["CRASH DATE"].dt.month
    df["year"] = df["CRASH DATE"].dt.year
    df["hour"] = pd.to_datetime(df["CRASH TIME"], format="%H:%M", errors="coerce").dt.hour
    df["dow"] = df["CRASH DATE"].dt.dayofweek

    # Assign season
    season_map = {12: "Winter", 1: "Winter", 2: "Winter",
                  3: "Spring", 4: "Spring", 5: "Spring",
                  6: "Summer", 7: "Summer", 8: "Summer",
                  9: "Fall", 10: "Fall", 11: "Fall"}
    df["season"] = df["month"].map(season_map)

    logger.info(f"Loaded {len(df)} crash records, years {df['year'].min()}-{df['year'].max()}")
    return df


def compute_monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly demand statistics."""
    # Count crashes per month (across all years)
    monthly = df.groupby("month").size().reset_index(name="total_crashes")

    # Count unique year-months for proper rate calculation
    df["year_month"] = df["CRASH DATE"].dt.to_period("M")
    n_periods = df.groupby("month")["year_month"].nunique().reset_index(name="n_months")
    monthly = monthly.merge(n_periods, on="month")

    monthly["avg_crashes_per_month"] = monthly["total_crashes"] / monthly["n_months"]
    monthly["avg_daily_rate"] = monthly["avg_crashes_per_month"] / 30.44  # avg days/month
    monthly["avg_hourly_rate"] = monthly["avg_daily_rate"] / 24.0

    # Overall average
    overall_avg = monthly["avg_crashes_per_month"].mean()
    monthly["factor"] = monthly["avg_crashes_per_month"] / overall_avg
    monthly["month_name"] = monthly["month"].map(dict(enumerate(MONTH_NAMES, 1)))

    # Assign season
    season_map = {12: "Winter", 1: "Winter", 2: "Winter",
                  3: "Spring", 4: "Spring", 5: "Spring",
                  6: "Summer", 7: "Summer", 8: "Summer",
                  9: "Fall", 10: "Fall", 11: "Fall"}
    monthly["season"] = monthly["month"].map(season_map)

    return monthly


def statistical_tests(df: pd.DataFrame, monthly: pd.DataFrame) -> dict:
    """Perform statistical tests for seasonal effects."""
    results = {}

    # 1. Chi-square test for uniformity across months
    observed = monthly["total_crashes"].values
    expected = np.full(12, observed.sum() / 12)
    chi2, p_chi2 = stats.chisquare(observed, expected)
    results["chi_square"] = {"statistic": chi2, "p_value": p_chi2, "df": 11}

    # 2. ANOVA across months (using year-month counts)
    df["year_month_str"] = df["CRASH DATE"].dt.to_period("M").astype(str)
    ym_counts = df.groupby(["month", "year_month_str"]).size().reset_index(name="count")
    month_groups = [grp["count"].values for _, grp in ym_counts.groupby("month")]
    f_stat, p_anova = stats.f_oneway(*month_groups)
    results["anova"] = {"F_statistic": f_stat, "p_value": p_anova, "df_between": 11}

    # 3. Kruskal-Wallis (non-parametric)
    h_stat, p_kw = stats.kruskal(*month_groups)
    results["kruskal_wallis"] = {"H_statistic": h_stat, "p_value": p_kw}

    # 4. Coefficient of variation
    monthly_rates = monthly["avg_crashes_per_month"].values
    cv = np.std(monthly_rates) / np.mean(monthly_rates)
    results["coefficient_of_variation"] = cv

    # 5. Seasonal amplitude
    peak = monthly_rates.max()
    trough = monthly_rates.min()
    amplitude = (peak - trough) / np.mean(monthly_rates)
    results["seasonal_amplitude"] = amplitude
    results["peak_month"] = MONTH_NAMES[np.argmax(monthly_rates)]
    results["trough_month"] = MONTH_NAMES[np.argmin(monthly_rates)]
    results["peak_factor"] = monthly["factor"].max()
    results["trough_factor"] = monthly["factor"].min()

    return results


def plot_monthly_patterns(monthly: pd.DataFrame, test_results: dict, save_path: Path):
    """Monthly demand bar chart with error bars."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Bar chart of average monthly crashes
    ax = axes[0]
    colors = [SEASON_COLORS[monthly.loc[monthly["month"] == m, "season"].iloc[0]]
              for m in range(1, 13)]

    bars = ax.bar(range(12), monthly.sort_values("month")["avg_crashes_per_month"],
                  color=colors, edgecolor="white", linewidth=0.5)

    overall_mean = monthly["avg_crashes_per_month"].mean()
    ax.axhline(overall_mean, color="black", linestyle="--", linewidth=1.5,
               label=f"Annual mean: {overall_mean:.0f}")

    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_NAMES, rotation=45)
    ax.set_ylabel("Average Crashes per Month")
    ax.set_title("Monthly Crash Demand", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Add season legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=s) for s, c in SEASON_COLORS.items()]
    ax.legend(handles=legend_elements + [plt.Line2D([0], [0], color="black", linestyle="--",
              label=f"Mean: {overall_mean:.0f}")], loc="upper left", fontsize=9)

    # Factor plot
    ax = axes[1]
    factors = monthly.sort_values("month")["factor"].values
    ax.bar(range(12), factors, color=colors, edgecolor="white", linewidth=0.5)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.5, label="Unity (no variation)")
    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_NAMES, rotation=45)
    ax.set_ylabel("Monthly Factor (relative to annual mean)")
    ax.set_title("Seasonal Demand Factors", fontweight="bold")
    ax.set_ylim(0.8, 1.2)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Add stats annotation
    cv = test_results["coefficient_of_variation"]
    amp = test_results["seasonal_amplitude"]
    ax.text(0.98, 0.02,
            f"CV = {cv:.3f}\nAmplitude = {amp:.3f}\nPeak: {test_results['peak_month']}\nTrough: {test_results['trough_month']}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))

    fig.suptitle("Seasonal Patterns in Manhattan Crash Demand", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Saved {save_path}")


def plot_seasonal_decomposition(df: pd.DataFrame, save_path: Path):
    """Time series decomposition: trend, seasonal, residual."""
    # Monthly time series
    ts = df.groupby(df["CRASH DATE"].dt.to_period("M")).size()
    ts.index = ts.index.to_timestamp()
    ts = ts.sort_index()

    # Simple decomposition using rolling mean
    window = 12
    if len(ts) < window * 2:
        logger.warning("Not enough data for decomposition")
        return

    trend = ts.rolling(window=window, center=True).mean()
    detrended = ts - trend
    # Average seasonal component
    seasonal_avg = detrended.groupby(detrended.index.month).mean()
    seasonal = pd.Series(
        [seasonal_avg.get(m, 0) for m in ts.index.month],
        index=ts.index
    )
    residual = ts - trend - seasonal

    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)

    axes[0].plot(ts.index, ts.values, "b-", linewidth=0.8)
    axes[0].set_ylabel("Monthly Crashes")
    axes[0].set_title("Observed", fontweight="bold")
    axes[0].grid(alpha=0.3)

    axes[1].plot(ts.index, trend.values, "r-", linewidth=1.5)
    axes[1].set_ylabel("Trend")
    axes[1].set_title("Trend (12-month rolling mean)", fontweight="bold")
    axes[1].grid(alpha=0.3)

    axes[2].plot(ts.index, seasonal.values, "g-", linewidth=0.8)
    axes[2].axhline(0, color="black", linestyle="--", linewidth=0.5)
    axes[2].set_ylabel("Seasonal")
    axes[2].set_title("Seasonal Component", fontweight="bold")
    axes[2].grid(alpha=0.3)

    axes[3].plot(ts.index, residual.values, "gray", linewidth=0.5)
    axes[3].axhline(0, color="black", linestyle="--", linewidth=0.5)
    axes[3].set_ylabel("Residual")
    axes[3].set_title("Residual", fontweight="bold")
    axes[3].grid(alpha=0.3)

    fig.suptitle("Seasonal Decomposition of Manhattan Crash Demand", fontweight="bold", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Saved {save_path}")


def plot_seasonal_heatmap(df: pd.DataFrame, save_path: Path):
    """Heatmap of demand by month and hour."""
    # Cross-tabulation of hour × month
    df_valid = df.dropna(subset=["hour", "month"])
    pivot = df_valid.groupby(["month", "hour"]).size().unstack(fill_value=0)

    # Normalize by number of occurrences
    n_years = df_valid["year"].nunique()
    days_per_month = df_valid.groupby("month")["CRASH DATE"].apply(lambda x: x.dt.date.nunique())
    for m in pivot.index:
        if m in days_per_month.index and days_per_month[m] > 0:
            pivot.loc[m] = pivot.loc[m] / days_per_month[m]

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, cmap="YlOrRd", ax=ax, annot=False, fmt=".1f",
                xticklabels=[f"{h:02d}" for h in range(24)],
                yticklabels=MONTH_NAMES,
                cbar_kws={"label": "Avg crashes per day"})
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Month")
    ax.set_title("Demand Heatmap: Month × Hour of Day", fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    logger.info(f"Saved {save_path}")


def main():
    logger.info("=" * 60)
    logger.info("SEASONAL PATTERN ANALYSIS")
    logger.info("=" * 60)

    # Load data
    df = load_crash_data()

    # Monthly statistics
    monthly = compute_monthly_stats(df)
    logger.info(f"\nMonthly crash rates:")
    for _, row in monthly.sort_values("month").iterrows():
        logger.info(f"  {row['month_name']:>3}: {row['avg_crashes_per_month']:.0f} crashes/month (factor={row['factor']:.3f})")

    # Statistical tests
    test_results = statistical_tests(df, monthly)

    logger.info(f"\nStatistical Tests:")
    logger.info(f"  Chi-square: χ²={test_results['chi_square']['statistic']:.1f}, p={test_results['chi_square']['p_value']:.4e}")
    logger.info(f"  ANOVA: F={test_results['anova']['F_statistic']:.2f}, p={test_results['anova']['p_value']:.4e}")
    logger.info(f"  Kruskal-Wallis: H={test_results['kruskal_wallis']['H_statistic']:.2f}, p={test_results['kruskal_wallis']['p_value']:.4e}")
    logger.info(f"  Coefficient of variation: {test_results['coefficient_of_variation']:.4f}")
    logger.info(f"  Seasonal amplitude: {test_results['seasonal_amplitude']:.4f}")
    logger.info(f"  Peak month: {test_results['peak_month']} (factor={test_results['peak_factor']:.3f})")
    logger.info(f"  Trough month: {test_results['trough_month']} (factor={test_results['trough_factor']:.3f})")

    # Save results table
    results_table = monthly[["month", "month_name", "season", "total_crashes",
                             "n_months", "avg_crashes_per_month", "avg_daily_rate",
                             "avg_hourly_rate", "factor"]].sort_values("month")

    # Add test summary row
    test_summary = pd.DataFrame([{
        "month": -1, "month_name": "TESTS",
        "season": f"CV={test_results['coefficient_of_variation']:.4f}",
        "total_crashes": int(df.shape[0]),
        "n_months": 0,
        "avg_crashes_per_month": monthly["avg_crashes_per_month"].mean(),
        "avg_daily_rate": monthly["avg_daily_rate"].mean(),
        "avg_hourly_rate": monthly["avg_hourly_rate"].mean(),
        "factor": 1.0,
    }])
    results_table = pd.concat([results_table, test_summary], ignore_index=True)
    results_table.to_csv(TABLES_DIR / "seasonal_analysis.csv", index=False)
    logger.info(f"\nSaved seasonal analysis to {TABLES_DIR / 'seasonal_analysis.csv'}")

    # Generate visualizations
    plot_monthly_patterns(monthly, test_results, FIGURES_DIR / "seasonal_patterns.png")
    plot_seasonal_decomposition(df, FIGURES_DIR / "seasonal_decomposition.png")
    plot_seasonal_heatmap(df, FIGURES_DIR / "seasonal_heatmap.png")

    # Summary interpretation
    cv = test_results["coefficient_of_variation"]
    logger.info(f"\n{'='*60}")
    logger.info("INTERPRETATION")
    logger.info(f"{'='*60}")
    if cv < 0.05:
        logger.info("Seasonal variation is MINIMAL (CV < 5%).")
        logger.info("The use of an annual average rate in the NHPP model is JUSTIFIED.")
        logger.info("Monthly factors range from {:.3f} to {:.3f}.".format(
            test_results["trough_factor"], test_results["peak_factor"]))
    elif cv < 0.15:
        logger.info("Seasonal variation is MODERATE (5% < CV < 15%).")
        logger.info("The annual average is a reasonable approximation.")
        logger.info("Consider seasonal adjustments for high-fidelity models.")
    else:
        logger.info("Seasonal variation is SIGNIFICANT (CV > 15%).")
        logger.info("Consider implementing seasonal-specific demand models.")

    logger.info("\nSeasonal analysis complete!")


if __name__ == "__main__":
    main()
