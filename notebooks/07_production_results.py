# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Phase 5 – Production Experiment Results
#
# Analysis of 1,440 simulation runs across four experiment sets:
# 1. **Exp 1**: Baseline policy comparison (P0, P1, P2 at K=20)
# 2. **Exp 2**: Fleet size sensitivity (K ∈ {15, 20, 25, 30, 35, 40})
# 3. **Exp 3**: Demand scaling sensitivity (δ ∈ {0.5–2.0})
# 4. **Exp 4**: Service time robustness (μ_s ∈ {20, 25, 30} min)

# %%
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Setup
PROJECT_ROOT = Path("..").resolve()
RESULTS_DIR = PROJECT_ROOT / "results" / "analysis" / "simulation" / "production"
FIGURES_DIR = PROJECT_ROOT / "results" / "analysis" / "figures"
TABLES_DIR = PROJECT_ROOT / "results" / "analysis" / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (10, 6),
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
})
sns.set_style("whitegrid")
PALETTE = {"P0": "#e74c3c", "P1": "#3498db", "P2": "#2ecc71"}

# %% [markdown]
# ## Load All Results

# %%
exp1 = pd.read_csv(RESULTS_DIR / "exp1_policy_comparison.csv")
exp2 = pd.read_csv(RESULTS_DIR / "exp2_fleet_sensitivity.csv")
exp3 = pd.read_csv(RESULTS_DIR / "exp3_demand_sensitivity.csv")
exp4 = pd.read_csv(RESULTS_DIR / "exp4_service_robustness.csv")

print(f"Exp 1: {len(exp1)} rows  |  Exp 2: {len(exp2)} rows")
print(f"Exp 3: {len(exp3)} rows  |  Exp 4: {len(exp4)} rows")
print(f"Total: {len(exp1)+len(exp2)+len(exp3)+len(exp4)} runs")

# %% [markdown]
# ## Helper Functions

# %%
def ci_summary(df, group_cols, metric_col, confidence=0.95):
    """Compute mean, std, and CI for a metric grouped by columns."""
    def _agg(x):
        n = len(x)
        m = x.mean()
        s = x.std(ddof=1) if n > 1 else 0
        if n > 1 and s > 0:
            t_crit = stats.t.ppf((1 + confidence) / 2, df=n - 1)
            margin = t_crit * s / np.sqrt(n)
        else:
            margin = 0
        return pd.Series({
            "mean": m, "std": s, "ci_lower": m - margin, "ci_upper": m + margin, "n": n
        })
    return df.groupby(group_cols)[metric_col].apply(_agg).unstack()


def paired_ttest(df, policy_a, policy_b, metric="mean_response_time"):
    """Paired t-test using CRN (same seeds)."""
    a = df[df["policy"] == policy_a].sort_values("replication")[metric].values
    b = df[df["policy"] == policy_b].sort_values("replication")[metric].values
    n = min(len(a), len(b))
    t_stat, p_val = stats.ttest_rel(a[:n], b[:n])
    diff = a[:n] - b[:n]
    d = diff.mean() / diff.std() if diff.std() > 0 else 0  # Cohen's d
    return {"t_stat": t_stat, "p_value": p_val, "cohens_d": d,
            "mean_diff": diff.mean(), "n": n}

# %% [markdown]
# ---
# ## Experiment 1: Baseline Policy Comparison

# %%
print("=== Exp 1: Policy Comparison (K=20, baseline conditions) ===\n")
exp1_summary = ci_summary(exp1, "policy", "mean_response_time")
print("Mean Response Time (minutes):")
print(exp1_summary.round(3).to_string())

# %%
# Coverage summary
cov_summary = ci_summary(exp1, "policy", "coverage_8min")
print("\n8-Minute Coverage:")
print(cov_summary.round(4).to_string())

# %%
# Paired t-tests
print("\n--- Paired T-Tests (CRN) ---")
for pa, pb in [("P0", "P1"), ("P0", "P2"), ("P1", "P2")]:
    r = paired_ttest(exp1, pa, pb)
    sig = "***" if r["p_value"] < 0.001 else "**" if r["p_value"] < 0.01 else "*" if r["p_value"] < 0.05 else "ns"
    print(f"  {pa} vs {pb}: diff={r['mean_diff']:+.3f} min, t={r['t_stat']:.2f}, "
          f"p={r['p_value']:.4f} {sig}, Cohen's d={r['cohens_d']:.2f}")

# %%
# Box plot – response time by policy
fig, axes = plt.subplots(1, 4, figsize=(20, 5))

# Response time
sns.boxplot(data=exp1, x="policy", y="mean_response_time", palette=PALETTE, ax=axes[0])
axes[0].set_title("Mean Response Time")
axes[0].set_ylabel("Minutes")
axes[0].set_xlabel("Policy")

# 6-min coverage (NYC)
if "coverage_6min" in exp1.columns:
    sns.boxplot(data=exp1, x="policy", y="coverage_6min", palette=PALETTE, ax=axes[1])
axes[1].set_title("6-Minute Coverage (NYC)")
axes[1].set_ylabel("Fraction")
axes[1].set_xlabel("Policy")

# 8-min coverage (NFPA)
sns.boxplot(data=exp1, x="policy", y="coverage_8min", palette=PALETTE, ax=axes[2])
axes[2].set_title("8-Minute Coverage (NFPA)")
axes[2].set_ylabel("Fraction")
axes[2].set_xlabel("Policy")

# P90 response time (90th percentile)
sns.boxplot(data=exp1, x="policy", y="p90_response_time", palette=PALETTE, ax=axes[3])
axes[3].set_title("P90 Response Time (90th percentile)")
axes[3].set_ylabel("Minutes")
axes[3].set_xlabel("Policy")

fig.suptitle("Experiment 1: Baseline Policy Comparison (K=20)", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "exp1_policy_comparison.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ---
# ## Experiment 2: Fleet Size Sensitivity

# %%
print("=== Exp 2: Fleet Size Sensitivity ===\n")
exp2_rt = ci_summary(exp2, ["policy", "K"], "mean_response_time")
print("Mean Response Time by Policy × K:")
print(exp2_rt.round(3).to_string())

# %%
# Line plot: mean RT vs K
fig, axes = plt.subplots(1, 4, figsize=(20, 5))

for policy in ["P0", "P1", "P2"]:
    sub = exp2[exp2["policy"] == policy]
    grp = sub.groupby("K")["mean_response_time"].agg(["mean", "std", "count"]).reset_index()
    t_crit = stats.t.ppf(0.975, df=grp["count"] - 1)
    grp["ci"] = t_crit * grp["std"] / np.sqrt(grp["count"])

    axes[0].errorbar(grp["K"], grp["mean"], yerr=grp["ci"], marker="o",
                     label=policy, color=PALETTE[policy], capsize=4)

axes[0].set_xlabel("Fleet Size (K)")
axes[0].set_ylabel("Mean Response Time (min)")
axes[0].set_title("Mean Response Time vs Fleet Size")
axes[0].legend()

# 6-min Coverage (NYC) vs K
if "coverage_6min" in exp2.columns:
    for policy in ["P0", "P1", "P2"]:
        sub = exp2[exp2["policy"] == policy]
        grp = sub.groupby("K")["coverage_6min"].agg(["mean", "std", "count"]).reset_index()
        t_crit = stats.t.ppf(0.975, df=grp["count"] - 1)
        grp["ci"] = t_crit * grp["std"] / np.sqrt(grp["count"])
        axes[1].errorbar(grp["K"], grp["mean"], yerr=grp["ci"], marker="D",
                         label=policy, color=PALETTE[policy], capsize=4)

axes[1].set_xlabel("Fleet Size (K)")
axes[1].set_ylabel("6-min Coverage (NYC)")
axes[1].set_title("6-min Coverage vs Fleet Size")
axes[1].legend()
axes[1].set_ylim(0, 1.05)

# 8-min Coverage (NFPA) vs K
for policy in ["P0", "P1", "P2"]:
    sub = exp2[exp2["policy"] == policy]
    grp = sub.groupby("K")["coverage_8min"].agg(["mean", "std", "count"]).reset_index()
    t_crit = stats.t.ppf(0.975, df=grp["count"] - 1)
    grp["ci"] = t_crit * grp["std"] / np.sqrt(grp["count"])

    axes[2].errorbar(grp["K"], grp["mean"], yerr=grp["ci"], marker="s",
                     label=policy, color=PALETTE[policy], capsize=4)

axes[2].set_xlabel("Fleet Size (K)")
axes[2].set_ylabel("8-min Coverage (NFPA)")
axes[2].set_title("C. 8-min Coverage (NFPA) vs Fleet Size")
axes[2].legend()
axes[2].set_ylim(0, 1.05)

# Utilization vs K
for policy in ["P0", "P1", "P2"]:
    sub = exp2[exp2["policy"] == policy]
    grp = sub.groupby("K")["mean_utilization"].agg(["mean"]).reset_index()
    axes[3].plot(grp["K"], grp["mean"], marker="^", label=policy, color=PALETTE[policy])

axes[3].set_xlabel("Fleet Size (K)")
axes[3].set_ylabel("Mean Utilization")
axes[3].set_title("Utilization vs Fleet Size")
axes[3].legend()

fig.suptitle("Experiment 2: Fleet Size Sensitivity", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "exp2_fleet_sensitivity.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ---
# ## Experiment 3: Demand Scaling Sensitivity

# %%
print("=== Exp 3: Demand Scaling Sensitivity ===\n")
exp3_rt = ci_summary(exp3, ["policy", "demand_multiplier"], "mean_response_time")
print("Mean Response Time by Policy × Demand Multiplier:")
print(exp3_rt.round(3).to_string())

# %%
fig, axes = plt.subplots(1, 4, figsize=(20, 5))

# RT vs demand multiplier
for policy in ["P0", "P1", "P2"]:
    sub = exp3[exp3["policy"] == policy]
    grp = sub.groupby("demand_multiplier")["mean_response_time"].agg(["mean", "std", "count"]).reset_index()
    t_crit = stats.t.ppf(0.975, df=grp["count"] - 1)
    grp["ci"] = t_crit * grp["std"] / np.sqrt(grp["count"])
    axes[0].errorbar(grp["demand_multiplier"], grp["mean"], yerr=grp["ci"],
                     marker="o", label=policy, color=PALETTE[policy], capsize=4)

axes[0].set_xlabel("Demand Multiplier")
axes[0].set_ylabel("Mean Response Time (min)")
axes[0].set_title("Response Time vs Demand")
axes[0].legend()

# 6-min Coverage (NYC) vs demand
if "coverage_6min" in exp3.columns:
    for policy in ["P0", "P1", "P2"]:
        sub = exp3[exp3["policy"] == policy]
        grp = sub.groupby("demand_multiplier")["coverage_6min"].agg(["mean"]).reset_index()
        axes[1].plot(grp["demand_multiplier"], grp["mean"], marker="D",
                     label=policy, color=PALETTE[policy])

axes[1].set_xlabel("Demand Multiplier")
axes[1].set_ylabel("6-min Coverage (NYC)")
axes[1].set_title("6-min Coverage vs Demand")
axes[1].legend()

# 8-min Coverage (NFPA) vs demand
for policy in ["P0", "P1", "P2"]:
    sub = exp3[exp3["policy"] == policy]
    grp = sub.groupby("demand_multiplier")["coverage_8min"].agg(["mean"]).reset_index()
    axes[2].plot(grp["demand_multiplier"], grp["mean"], marker="s",
                 label=policy, color=PALETTE[policy])

axes[2].set_xlabel("Demand Multiplier")
axes[2].set_ylabel("8-min Coverage (NFPA)")
axes[2].set_title("C. 8-min Coverage (NFPA) vs Demand")
axes[2].legend()

# Queue fraction vs demand
for policy in ["P0", "P1", "P2"]:
    sub = exp3[exp3["policy"] == policy]
    grp = sub.groupby("demand_multiplier")["queue_fraction"].agg(["mean"]).reset_index()
    axes[3].plot(grp["demand_multiplier"], grp["mean"], marker="^",
                 label=policy, color=PALETTE[policy])

axes[3].set_xlabel("Demand Multiplier")
axes[3].set_ylabel("Queue Fraction")
axes[3].set_title("Queueing vs Demand")
axes[3].legend()

fig.suptitle("Experiment 3: Demand Scaling Sensitivity (K=20)", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "exp3_demand_sensitivity.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ---
# ## Experiment 4: Service Time Robustness

# %%
print("=== Exp 4: Service Time Robustness ===\n")
exp4_rt = ci_summary(exp4, ["policy", "service_time_mean"], "mean_response_time")
print("Mean Response Time by Policy × Service Time Mean:")
print(exp4_rt.round(3).to_string())

# %%
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# RT by service time
for policy in ["P0", "P1", "P2"]:
    sub = exp4[exp4["policy"] == policy]
    grp = sub.groupby("service_time_mean")["mean_response_time"].agg(["mean", "std", "count"]).reset_index()
    t_crit = stats.t.ppf(0.975, df=grp["count"] - 1)
    grp["ci"] = t_crit * grp["std"] / np.sqrt(grp["count"])
    axes[0].errorbar(grp["service_time_mean"], grp["mean"], yerr=grp["ci"],
                     marker="o", label=policy, color=PALETTE[policy], capsize=4)

axes[0].set_xlabel("Service Time Mean (min)")
axes[0].set_ylabel("Mean Response Time (min)")
axes[0].set_title("A. Response Time vs Service Duration")
axes[0].legend()

# 6-min Coverage (NYC) by service time
for policy in ["P0", "P1", "P2"]:
    sub = exp4[exp4["policy"] == policy]
    grp = sub.groupby("service_time_mean")["coverage_6min"].agg(["mean"]).reset_index()
    axes[1].plot(grp["service_time_mean"], grp["mean"], marker="s",
                 label=policy, color=PALETTE[policy])

axes[1].set_xlabel("Service Time Mean (min)")
axes[1].set_ylabel("6-min Coverage (NYC)")
axes[1].set_title("B. 6-min Coverage (NYC) vs Service Duration")
axes[1].legend()

# 8-min Coverage (NFPA) by service time
for policy in ["P0", "P1", "P2"]:
    sub = exp4[exp4["policy"] == policy]
    grp = sub.groupby("service_time_mean")["coverage_8min"].agg(["mean"]).reset_index()
    axes[2].plot(grp["service_time_mean"], grp["mean"], marker="s",
                 label=policy, color=PALETTE[policy])

axes[2].set_xlabel("Service Time Mean (min)")
axes[2].set_ylabel("8-min Coverage (NFPA)")
axes[2].set_title("C. 8-min Coverage (NFPA) vs Service Duration")
axes[2].legend()

fig.suptitle("Experiment 4: Service Time Robustness (K=20)", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "exp4_service_robustness.png", dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ---
# ## Combined Summary Table

# %%
# Build comprehensive summary table
def build_summary_table(df, exp_name, extra_cols=None):
    """Build a summary table with CIs for all key metrics."""
    group_cols = ["policy"]
    if extra_cols:
        group_cols = group_cols + extra_cols

    metrics = {
        "mean_response_time": "Mean RT (min)",
        "p90_response_time": "P90 Response Time (90th pctl, min)",
        "coverage_6min": "6-min Coverage (NYC)",
        "coverage_8min": "8-min Coverage (NFPA)",
        "mean_utilization": "Mean Utilization",
        "queue_fraction": "Queue Fraction",
    }

    rows = []
    for name, grp in df.groupby(group_cols):
        if not isinstance(name, tuple):
            name = (name,)
        row = dict(zip(group_cols, name))
        row["n_reps"] = len(grp)
        for col, label in metrics.items():
            vals = grp[col].values
            m = vals.mean()
            s = vals.std(ddof=1) if len(vals) > 1 else 0
            n = len(vals)
            if n > 1 and s > 0:
                t_c = stats.t.ppf(0.975, df=n - 1)
                margin = t_c * s / np.sqrt(n)
            else:
                margin = 0
            row[f"{label}"] = f"{m:.3f}"
            row[f"{label} 95% CI"] = f"[{m-margin:.3f}, {m+margin:.3f}]"
        rows.append(row)

    return pd.DataFrame(rows)


# Exp 1 summary table
print("=== Experiment 1 Summary ===")
t1 = build_summary_table(exp1, "exp1")
print(t1.to_string(index=False))
t1.to_csv(TABLES_DIR / "exp1_summary.csv", index=False)

# %%
# Exp 2 pivot table
print("\n=== Experiment 2: Mean RT by Policy × K ===")
t2_pivot = exp2.pivot_table(
    values="mean_response_time", index="K", columns="policy", aggfunc="mean"
)[["P0", "P1", "P2"]]
print(t2_pivot.round(3).to_string())
t2_pivot.to_csv(TABLES_DIR / "exp2_pivot_rt.csv")

# %%
# Exp 3 pivot table
print("\n=== Experiment 3: Mean RT by Policy × Demand Multiplier ===")
t3_pivot = exp3.pivot_table(
    values="mean_response_time", index="demand_multiplier", columns="policy", aggfunc="mean"
)[["P0", "P1", "P2"]]
print(t3_pivot.round(3).to_string())
t3_pivot.to_csv(TABLES_DIR / "exp3_pivot_rt.csv")

# %%
# Exp 4 summary
print("\n=== Experiment 4: Mean RT by Policy × Service Time ===")
t4_pivot = exp4.pivot_table(
    values="mean_response_time", index="service_time_mean", columns="policy", aggfunc="mean"
)[["P0", "P1", "P2"]]
print(t4_pivot.round(3).to_string())
t4_pivot.to_csv(TABLES_DIR / "exp4_pivot_rt.csv")

# %% [markdown]
# ---
# ## Key Findings

# %%
print("=" * 60)
print("KEY FINDINGS")
print("=" * 60)

# Exp 1 findings
p0_rt = exp1[exp1["policy"] == "P0"]["mean_response_time"].mean()
p1_rt = exp1[exp1["policy"] == "P1"]["mean_response_time"].mean()
p2_rt = exp1[exp1["policy"] == "P2"]["mean_response_time"].mean()
print(f"\n1. Baseline Policy Comparison (K=20):")
print(f"   P0 mean RT: {p0_rt:.2f} min | P1: {p1_rt:.2f} min | P2: {p2_rt:.2f} min")
print(f"   P2 improvement over P0: {(1-p2_rt/p0_rt)*100:.1f}%")
print(f"   P2 improvement over P1: {(1-p2_rt/p1_rt)*100:.1f}%")

# Exp 2 findings
print(f"\n2. Fleet Size Sensitivity:")
for K in sorted(exp2["K"].unique()):
    p2_val = exp2[(exp2["policy"]=="P2") & (exp2["K"]==K)]["mean_response_time"].mean()
    p0_val = exp2[(exp2["policy"]=="P0") & (exp2["K"]==K)]["mean_response_time"].mean()
    print(f"   K={K:2d}: P0={p0_val:.2f}, P2={p2_val:.2f} min (P2 advantage: {p0_val-p2_val:.2f} min)")

# Exp 3 findings
print(f"\n3. Demand Scaling Sensitivity:")
for dm in sorted(exp3["demand_multiplier"].unique()):
    p2_val = exp3[(exp3["policy"]=="P2") & (exp3["demand_multiplier"]==dm)]["mean_response_time"].mean()
    p0_val = exp3[(exp3["policy"]=="P0") & (exp3["demand_multiplier"]==dm)]["mean_response_time"].mean()
    print(f"   δ={dm:.2f}: P0={p0_val:.2f}, P2={p2_val:.2f} min")

# Exp 4 findings
print(f"\n4. Service Time Robustness:")
for sm in sorted(exp4["service_time_mean"].unique()):
    p2_val = exp4[(exp4["policy"]=="P2") & (exp4["service_time_mean"]==sm)]["mean_response_time"].mean()
    p0_val = exp4[(exp4["policy"]=="P0") & (exp4["service_time_mean"]==sm)]["mean_response_time"].mean()
    print(f"   μ_s={sm:.0f} min: P0={p0_val:.2f}, P2={p2_val:.2f} min")

print(f"\n{'='*60}")
print("All production experiments completed successfully.")
print(f"Total runs: {len(exp1)+len(exp2)+len(exp3)+len(exp4)}")
