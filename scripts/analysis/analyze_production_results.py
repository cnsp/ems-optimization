#!/usr/bin/env python3
"""
Phase 6 – Comprehensive Statistical Analysis of Production Results
===================================================================

Reads the four experiment CSVs produced by Phase 5 and generates:
    • Descriptive statistics          → results/tables/descriptive_statistics.csv
    • ANOVA results                   → results/tables/anova_results.csv
    • Post-hoc pairwise comparisons   → results/tables/posthoc_comparisons.csv
    • Confidence intervals            → results/tables/confidence_intervals.csv
    • Effect sizes (Cohen's d, η²)    → results/tables/effect_sizes.csv
    • Sensitivity analysis summary    → results/tables/sensitivity_summary.csv
    • Publication tables 1–4          → results/tables/table{1..4}_*.csv / .tex
"""
from __future__ import annotations
import os, sys, warnings, itertools, textwrap
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# ---------------------------------------------------------------------------
# Optional imports – degrade gracefully
# ---------------------------------------------------------------------------
try:
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    from statsmodels.stats.anova import anova_lm
    HAS_SM = True
except ImportError:
    HAS_SM = False
    warnings.warn("statsmodels not installed – ANOVA / Tukey will use SciPy fallback")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT / "results" / "simulation" / "production"
CAPACITY = 5  # v1 production experiments used capacity=5 (implicit default)
TABLE_DIR = PROJECT / "results" / "tables"
TABLE_DIR.mkdir(parents=True, exist_ok=True)

METRICS = ["mean_response_time", "p90_response_time", "coverage_6min", "coverage_8min", "mean_utilization"]
METRIC_LABELS = {
    "mean_response_time": "Mean RT (min)",
    "p90_response_time": "P90 Response Time (90th percentile, min)",
    "coverage_6min": "6-min Coverage (NYC)",
    "coverage_8min": "8-min Coverage (NFPA)",
    "mean_utilization": "Mean Utilization",
}


# ===================================================================
# Helpers
# ===================================================================
def load_experiment(name: str) -> pd.DataFrame:
    path = DATA_DIR / f"{name}.csv"
    if not path.exists():
        sys.exit(f"ERROR: {path} not found.")
    return pd.read_csv(path)


def cohens_d(a, b):
    """Compute Cohen's d (pooled SD)."""
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    if sp == 0:
        return 0.0
    return (np.mean(a) - np.mean(b)) / sp


def d_interpretation(d):
    d = abs(d)
    if d < 0.2:   return "Negligible"
    if d < 0.5:   return "Small"
    if d < 0.8:   return "Medium"
    return "Large"


def eta_sq_interpretation(eta2):
    if eta2 < 0.01:  return "Negligible"
    if eta2 < 0.06:  return "Small"
    if eta2 < 0.14:  return "Medium"
    return "Large"


def sig_stars(p):
    if p < 0.001:  return "***"
    if p < 0.01:   return "**"
    if p < 0.05:   return "*"
    return "ns"


def to_latex_table(df: pd.DataFrame, caption: str, label: str) -> str:
    """Quick LaTeX tabular export."""
    ncols = len(df.columns)
    col_fmt = "l" + "r" * (ncols - 1)
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        rf"\begin{{tabular}}{{{col_fmt}}}",
        r"\toprule",
        " & ".join(df.columns) + r" \\",
        r"\midrule",
    ]
    for _, row in df.iterrows():
        lines.append(" & ".join(str(v) for v in row.values) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


# ===================================================================
# 1. Descriptive Statistics
# ===================================================================
def compute_descriptive(all_data: pd.DataFrame) -> pd.DataFrame:
    print("\n=== 1. Descriptive Statistics ===")
    rows = []
    for (exp, pol), grp in all_data.groupby(["experiment_id", "policy"]):
        for m in METRICS:
            vals = grp[m].dropna()
            rows.append({
                "Experiment": exp, "Policy": pol, "Metric": METRIC_LABELS.get(m, m),
                "N": len(vals),
                "Mean": round(vals.mean(), 4),
                "Std": round(vals.std(), 4),
                "Min": round(vals.min(), 4),
                "Q1": round(vals.quantile(0.25), 4),
                "Median": round(vals.median(), 4),
                "Q3": round(vals.quantile(0.75), 4),
                "Max": round(vals.max(), 4),
                "IQR": round(vals.quantile(0.75) - vals.quantile(0.25), 4),
                "CV": round(vals.std() / vals.mean(), 4) if vals.mean() != 0 else 0.0,
            })
    df = pd.DataFrame(rows)
    path = TABLE_DIR / "descriptive_statistics.csv"
    df.to_csv(path, index=False)
    print(f"  → Saved {path}  ({len(df)} rows)")
    return df


# ===================================================================
# 2. ANOVA
# ===================================================================
def run_anova(all_data: pd.DataFrame) -> pd.DataFrame:
    print("\n=== 2. ANOVA ===")
    anova_rows = []

    # --- Exp 1: One-way ANOVA ---
    exp1 = all_data[all_data["experiment_id"] == "exp1_policy_comparison"]
    for m in METRICS:
        groups = [g[m].values for _, g in exp1.groupby("policy")]
        F, p = stats.f_oneway(*groups)
        ss_between = sum(len(g) * (g.mean() - exp1[m].mean())**2 for g in [pd.Series(g) for g in groups])
        ss_total = ((exp1[m] - exp1[m].mean())**2).sum()
        eta2 = ss_between / ss_total if ss_total > 0 else 0

        # Assumption checks
        residuals = exp1[m] - exp1.groupby("policy")[m].transform("mean")
        _, p_shapiro = stats.shapiro(residuals)
        _, p_levene = stats.levene(*groups)

        anova_rows.append({
            "Experiment": "Exp1", "Factor(s)": "Policy", "Metric": METRIC_LABELS.get(m, m),
            "F": round(F, 3), "p_value": round(p, 6), "Significance": sig_stars(p),
            "Eta_squared": round(eta2, 4), "Effect": eta_sq_interpretation(eta2),
            "Shapiro_p": round(p_shapiro, 4), "Levene_p": round(p_levene, 4),
        })

    # --- Exp 2–4: Two-way ANOVA (SciPy fallback if no statsmodels) ---
    two_way_specs = [
        ("exp2_fleet_sensitivity", "Exp2", "K", "Policy × K"),
        ("exp3_demand_sensitivity", "Exp3", "demand_multiplier", "Policy × Demand"),
        ("exp4_service_robustness", "Exp4", "service_time_mean", "Policy × ServiceTime"),
    ]
    for exp_id, exp_label, factor_col, factor_desc in two_way_specs:
        df_exp = all_data[all_data["experiment_id"] == exp_id].copy()
        df_exp["FactorB"] = df_exp[factor_col].astype(str)
        for m in METRICS:
            if HAS_SM:
                try:
                    model = ols(f"{m} ~ C(policy) * C(FactorB)", data=df_exp).fit()
                    aov = anova_lm(model, typ=2)
                    ss_total = aov["sum_sq"].sum()
                    for src in ["C(policy)", "C(FactorB)", "C(policy):C(FactorB)"]:
                        if src in aov.index:
                            row = aov.loc[src]
                            eta2 = row["sum_sq"] / ss_total
                            src_label = src.replace("C(policy)", "Policy").replace("C(FactorB)", factor_col).replace(":", " × ")
                            anova_rows.append({
                                "Experiment": exp_label, "Factor(s)": src_label,
                                "Metric": METRIC_LABELS.get(m, m),
                                "F": round(row["F"], 3), "p_value": round(row["PR(>F)"], 6),
                                "Significance": sig_stars(row["PR(>F)"]),
                                "Eta_squared": round(eta2, 4), "Effect": eta_sq_interpretation(eta2),
                                "Shapiro_p": np.nan, "Levene_p": np.nan,
                            })
                except Exception as e:
                    warnings.warn(f"statsmodels ANOVA failed for {exp_label}/{m}: {e}")
            else:
                # Fallback: one-way per factor
                groups = [g[m].values for _, g in df_exp.groupby("policy")]
                F, p = stats.f_oneway(*groups)
                ss_between = sum(len(g) * (g.mean() - df_exp[m].mean())**2 for g in [pd.Series(g) for g in groups])
                ss_total = ((df_exp[m] - df_exp[m].mean())**2).sum()
                eta2 = ss_between / ss_total if ss_total > 0 else 0
                anova_rows.append({
                    "Experiment": exp_label, "Factor(s)": "Policy (1-way fallback)",
                    "Metric": METRIC_LABELS.get(m, m),
                    "F": round(F, 3), "p_value": round(p, 6), "Significance": sig_stars(p),
                    "Eta_squared": round(eta2, 4), "Effect": eta_sq_interpretation(eta2),
                    "Shapiro_p": np.nan, "Levene_p": np.nan,
                })

    df_anova = pd.DataFrame(anova_rows)
    path = TABLE_DIR / "anova_results.csv"
    df_anova.to_csv(path, index=False)
    print(f"  → Saved {path}  ({len(df_anova)} rows)")
    return df_anova


# ===================================================================
# 3. Post-hoc Multiple Comparisons
# ===================================================================
def run_posthoc(all_data: pd.DataFrame) -> pd.DataFrame:
    print("\n=== 3. Post-hoc Comparisons ===")
    rows = []
    policies = sorted(all_data["policy"].unique())
    pairs = list(itertools.combinations(policies, 2))
    n_comp = len(pairs)

    for exp_id in all_data["experiment_id"].unique():
        df_exp = all_data[all_data["experiment_id"] == exp_id]
        for m in METRICS:
            # Tukey HSD (if statsmodels available)
            tukey_results = {}
            if HAS_SM:
                try:
                    tukey = pairwise_tukeyhsd(df_exp[m], df_exp["policy"], alpha=0.05)
                    for r in tukey.summary().data[1:]:
                        tukey_results[(r[0], r[1])] = {"meandiff": r[2], "p_tukey": r[3], "reject": r[5]}
                except Exception:
                    pass

            for pA, pB in pairs:
                a = df_exp.loc[df_exp["policy"] == pA, m].values
                b = df_exp.loc[df_exp["policy"] == pB, m].values
                if len(a) == 0 or len(b) == 0:
                    continue
                t_stat, p_raw = stats.ttest_ind(a, b)
                p_bonf = min(p_raw * n_comp, 1.0)
                d = cohens_d(a, b)
                mean_diff = np.mean(a) - np.mean(b)
                se_diff = np.sqrt(np.var(a, ddof=1)/len(a) + np.var(b, ddof=1)/len(b))
                t_crit = stats.t.ppf(0.975, min(len(a), len(b)) - 1)
                ci_lo = mean_diff - t_crit * se_diff
                ci_hi = mean_diff + t_crit * se_diff

                # Tukey p if available
                p_tukey = tukey_results.get((pA, pB), tukey_results.get((pB, pA), {})).get("p_tukey", np.nan)

                rows.append({
                    "Experiment": exp_id, "Metric": METRIC_LABELS.get(m, m),
                    "Policy_A": pA, "Policy_B": pB,
                    "Mean_A": round(np.mean(a), 4), "Mean_B": round(np.mean(b), 4),
                    "Mean_Diff": round(mean_diff, 4),
                    "CI_95_lo": round(ci_lo, 4), "CI_95_hi": round(ci_hi, 4),
                    "t_stat": round(t_stat, 3), "p_raw": round(p_raw, 6),
                    "p_bonferroni": round(p_bonf, 6),
                    "p_tukey": round(p_tukey, 6) if not np.isnan(p_tukey) else "",
                    "Cohens_d": round(d, 4), "Effect_Size": d_interpretation(d),
                    "Significance": sig_stars(p_bonf),
                })

    df_ph = pd.DataFrame(rows)
    path = TABLE_DIR / "posthoc_comparisons.csv"
    df_ph.to_csv(path, index=False)
    print(f"  → Saved {path}  ({len(df_ph)} rows)")
    return df_ph


# ===================================================================
# 4. Confidence Intervals
# ===================================================================
def compute_confidence_intervals(all_data: pd.DataFrame) -> pd.DataFrame:
    print("\n=== 4. Confidence Intervals ===")
    rows = []
    for (exp, pol), grp in all_data.groupby(["experiment_id", "policy"]):
        for m in METRICS:
            vals = grp[m].dropna()
            n = len(vals)
            mean = vals.mean()
            se = vals.std() / np.sqrt(n) if n > 1 else 0
            t_crit = stats.t.ppf(0.975, n - 1) if n > 1 else np.nan
            rows.append({
                "Experiment": exp, "Policy": pol, "Metric": METRIC_LABELS.get(m, m),
                "N": n, "Mean": round(mean, 4), "Std": round(vals.std(), 4),
                "SE": round(se, 4),
                "CI_95_lo": round(mean - t_crit * se, 4) if n > 1 else np.nan,
                "CI_95_hi": round(mean + t_crit * se, 4) if n > 1 else np.nan,
                "CI_width": round(2 * t_crit * se, 4) if n > 1 else np.nan,
            })
    df = pd.DataFrame(rows)
    path = TABLE_DIR / "confidence_intervals.csv"
    df.to_csv(path, index=False)
    print(f"  → Saved {path}  ({len(df)} rows)")
    return df


# ===================================================================
# 5. Effect Sizes
# ===================================================================
def compute_effect_sizes(all_data: pd.DataFrame, df_anova: pd.DataFrame) -> pd.DataFrame:
    print("\n=== 5. Effect Sizes ===")
    rows = []
    policies = sorted(all_data["policy"].unique())
    pairs = list(itertools.combinations(policies, 2))
    for exp_id in all_data["experiment_id"].unique():
        df_exp = all_data[all_data["experiment_id"] == exp_id]
        for m in METRICS:
            for pA, pB in pairs:
                a = df_exp.loc[df_exp["policy"] == pA, m].values
                b = df_exp.loc[df_exp["policy"] == pB, m].values
                if len(a) == 0 or len(b) == 0:
                    continue
                d = cohens_d(a, b)
                rows.append({
                    "Experiment": exp_id, "Metric": METRIC_LABELS.get(m, m),
                    "Comparison": f"{pA} vs {pB}",
                    "Cohens_d": round(d, 4),
                    "Abs_d": round(abs(d), 4),
                    "Interpretation": d_interpretation(d),
                    "Practical_Significance": "Yes" if abs(d) >= 0.5 else "No",
                })
    # Add η² from ANOVA table
    for _, row in df_anova.iterrows():
        rows.append({
            "Experiment": row["Experiment"], "Metric": row["Metric"],
            "Comparison": f"ANOVA: {row['Factor(s)']}",
            "Cohens_d": np.nan,
            "Abs_d": np.nan,
            "Interpretation": row["Effect"],
            "Practical_Significance": "Yes" if row["Eta_squared"] >= 0.06 else "No",
        })
    df = pd.DataFrame(rows)
    path = TABLE_DIR / "effect_sizes.csv"
    df.to_csv(path, index=False)
    print(f"  → Saved {path}  ({len(df)} rows)")
    return df


# ===================================================================
# 6. Sensitivity Summary
# ===================================================================
def compute_sensitivity_summary(all_data: pd.DataFrame) -> pd.DataFrame:
    print("\n=== 6. Sensitivity Summary ===")
    rows = []
    specs = [
        ("exp2_fleet_sensitivity", "K"),
        ("exp3_demand_sensitivity", "demand_multiplier"),
        ("exp4_service_robustness", "service_time_mean"),
    ]
    for exp_id, factor_col in specs:
        df_exp = all_data[all_data["experiment_id"] == exp_id]
        for (pol, lvl), grp in df_exp.groupby(["policy", factor_col]):
            for m in METRICS:
                vals = grp[m].dropna()
                rows.append({
                    "Experiment": exp_id, "Policy": pol,
                    "Factor": factor_col, "Level": lvl,
                    "Metric": METRIC_LABELS.get(m, m),
                    "Mean": round(vals.mean(), 4),
                    "Std": round(vals.std(), 4),
                    "CI_95_lo": round(vals.mean() - 1.96 * vals.std() / np.sqrt(len(vals)), 4),
                    "CI_95_hi": round(vals.mean() + 1.96 * vals.std() / np.sqrt(len(vals)), 4),
                })
    df = pd.DataFrame(rows)
    path = TABLE_DIR / "sensitivity_summary.csv"
    df.to_csv(path, index=False)
    print(f"  → Saved {path}  ({len(df)} rows)")
    return df


# ===================================================================
# 7. Publication Tables
# ===================================================================
def generate_publication_tables(all_data: pd.DataFrame, df_anova: pd.DataFrame,
                                 df_posthoc: pd.DataFrame, df_ci: pd.DataFrame) -> None:
    print("\n=== 7. Publication Tables ===")

    # --- Table 1: Baseline Policy Comparison ---
    exp1 = all_data[all_data["experiment_id"] == "exp1_policy_comparison"]
    ci1 = df_ci[df_ci["Experiment"] == "exp1_policy_comparison"]
    t1_rows = []
    for pol in ["P0", "P1", "P2"]:
        grp = exp1[exp1["policy"] == pol]
        ci_row_rt = ci1[(ci1["Policy"] == pol) & (ci1["Metric"] == "Mean RT (min)")]
        ci_lo = ci_row_rt["CI_95_lo"].values[0] if len(ci_row_rt) else ""
        ci_hi = ci_row_rt["CI_95_hi"].values[0] if len(ci_row_rt) else ""
        t1_rows.append({
            "Policy": pol,
            "Mean RT (95% CI)": f"{grp['mean_response_time'].mean():.2f} ({ci_lo}, {ci_hi})",
            "P90 Response Time (90th pctl)": f"{grp['p90_response_time'].mean():.2f}",
            "6-min Coverage (NYC)": f"{grp['coverage_6min'].mean():.1%}" if 'coverage_6min' in grp.columns else "N/A",
            "8-min Coverage (NFPA)": f"{grp['coverage_8min'].mean():.1%}",
            "Utilization": f"{grp['mean_utilization'].mean():.3f}",
            "N": len(grp),
        })
    t1 = pd.DataFrame(t1_rows)
    t1.to_csv(TABLE_DIR / "table1_baseline_comparison.csv", index=False)
    (TABLE_DIR / "table1_baseline_comparison.tex").write_text(
        to_latex_table(t1, f"Baseline Policy Comparison (Experiment 1, K=20, cap={CAPACITY})", "tab:baseline"))
    print(f"  → Table 1 saved")

    # --- Table 2: ANOVA Summary ---
    t2 = df_anova[["Experiment", "Factor(s)", "Metric", "F", "p_value", "Significance", "Eta_squared", "Effect"]].copy()
    t2.columns = ["Experiment", "Source", "Metric", "F", "p", "Sig.", "η²", "Effect"]
    t2.to_csv(TABLE_DIR / "table2_anova_summary.csv", index=False)
    (TABLE_DIR / "table2_anova_summary.tex").write_text(
        to_latex_table(t2, f"ANOVA Results Summary (cap={CAPACITY})", "tab:anova"))
    print(f"  → Table 2 saved")

    # --- Table 3: Pairwise Comparisons ---
    t3 = df_posthoc[df_posthoc["Experiment"] == "exp1_policy_comparison"][
        ["Metric", "Policy_A", "Policy_B", "Mean_Diff", "CI_95_lo", "CI_95_hi",
         "p_bonferroni", "Cohens_d", "Significance"]
    ].copy()
    t3.columns = ["Metric", "A", "B", "Δ Mean", "CI Lo", "CI Hi", "p (Bonf.)", "Cohen's d", "Sig."]
    t3.to_csv(TABLE_DIR / "table3_pairwise_comparisons.csv", index=False)
    (TABLE_DIR / "table3_pairwise_comparisons.tex").write_text(
        to_latex_table(t3, f"Pairwise Policy Comparisons (Experiment 1, cap={CAPACITY})", "tab:pairwise"))
    print(f"  → Table 3 saved")

    # --- Table 4: Sensitivity Summary (pivot) ---
    sens = all_data[all_data["experiment_id"].isin([
        "exp2_fleet_sensitivity", "exp3_demand_sensitivity", "exp4_service_robustness"
    ])]
    t4_rows = []
    for exp_id, factor_col in [("exp2_fleet_sensitivity", "K"),
                                 ("exp3_demand_sensitivity", "demand_multiplier"),
                                 ("exp4_service_robustness", "service_time_mean")]:
        df_exp = sens[sens["experiment_id"] == exp_id]
        for lvl in sorted(df_exp[factor_col].unique()):
            for pol in ["P0", "P1", "P2"]:
                grp = df_exp[(df_exp[factor_col] == lvl) & (df_exp["policy"] == pol)]
                if len(grp) == 0:
                    continue
                t4_rows.append({
                    "Experiment": exp_id.replace("exp2_fleet_sensitivity", "Fleet Size")
                                      .replace("exp3_demand_sensitivity", "Demand")
                                      .replace("exp4_service_robustness", "Service Time"),
                    "Factor Level": lvl, "Policy": pol,
                    "Mean RT": f"{grp['mean_response_time'].mean():.2f}",
                    "P90 RT (90th pctl)": f"{grp['p90_response_time'].mean():.2f}" if 'p90_response_time' in grp.columns else "N/A",
                    "6-min Coverage (NYC)": f"{grp['coverage_6min'].mean():.1%}" if 'coverage_6min' in grp.columns else "N/A",
                    "8-min Coverage (NFPA)": f"{grp['coverage_8min'].mean():.1%}",
                    "Utilization": f"{grp['mean_utilization'].mean():.3f}",
                })
    t4 = pd.DataFrame(t4_rows)
    t4.to_csv(TABLE_DIR / "table4_sensitivity_summary.csv", index=False)
    (TABLE_DIR / "table4_sensitivity_summary.tex").write_text(
        to_latex_table(t4, f"Sensitivity Analysis Summary (cap={CAPACITY})", "tab:sensitivity"))
    print(f"  → Table 4 saved")


# ===================================================================
# Main
# ===================================================================
def main():
    print("=" * 70)
    print("Phase 6 – Comprehensive Statistical Analysis")
    print("=" * 70)

    # Load all experiment data
    frames = []
    for name in ["exp1_policy_comparison", "exp2_fleet_sensitivity",
                  "exp3_demand_sensitivity", "exp4_service_robustness"]:
        frames.append(load_experiment(name))
    all_data = pd.concat(frames, ignore_index=True)
    print(f"\nLoaded {len(all_data)} rows across {all_data['experiment_id'].nunique()} experiments")
    print(f"Policies: {sorted(all_data['policy'].unique())}")

    desc = compute_descriptive(all_data)
    df_anova = run_anova(all_data)
    df_posthoc = run_posthoc(all_data)
    df_ci = compute_confidence_intervals(all_data)
    df_effect = compute_effect_sizes(all_data, df_anova)
    df_sens = compute_sensitivity_summary(all_data)
    generate_publication_tables(all_data, df_anova, df_posthoc, df_ci)

    print("\n" + "=" * 70)
    print("Analysis complete. All outputs in results/tables/")
    print("=" * 70)


if __name__ == "__main__":
    main()
