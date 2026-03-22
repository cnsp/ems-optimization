#!/usr/bin/env python3
"""
Controlled regeneration wrapper.
Runs each analysis script with output redirected to tmp/regenerated_compare/.
Does NOT modify any existing files.
"""
import sys, os, importlib, traceback
from pathlib import Path
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT))

TMP_OUT = PROJECT / "tmp" / "regenerated_compare"
TMP_FIG = TMP_OUT / "figures"
TMP_TAB = TMP_OUT / "tables"
TMP_FIG.mkdir(parents=True, exist_ok=True)
TMP_TAB.mkdir(parents=True, exist_ok=True)

results = {}

# ─── 1. Capacity Sensitivity Heatmap ───
print("\n" + "="*60)
print("1. Capacity Sensitivity Heatmap")
print("="*60)
try:
    import scripts.analysis.generate_capacity_sensitivity_heatmap as cap_mod
    importlib.reload(cap_mod)
    # Redirect FIGURES_DIR
    cap_mod.FIGURES_DIR = TMP_FIG
    # Call main
    cap_mod.main()
    results["capacity_sensitivity_heatmap"] = "SUCCESS"
except Exception as e:
    results["capacity_sensitivity_heatmap"] = f"FAILED: {e}"
    traceback.print_exc()

# ─── 2. Queue Metrics ───
print("\n" + "="*60)
print("2. Queue Metrics Analysis")
print("="*60)
try:
    import scripts.analysis.analyze_queue_metrics as queue_mod
    importlib.reload(queue_mod)
    queue_mod.FIGURES_DIR = TMP_FIG
    queue_mod.TABLES_DIR = TMP_TAB
    queue_mod.main()
    results["queue_metrics"] = "SUCCESS"
except Exception as e:
    results["queue_metrics"] = f"FAILED: {e}"
    traceback.print_exc()

# ─── 3. Publication Figures ───
print("\n" + "="*60)
print("3. Publication Figures")
print("="*60)
try:
    import scripts.analysis.generate_publication_figures as pub_mod
    importlib.reload(pub_mod)
    pub_mod.FIG_DIR = TMP_FIG
    pub_mod.main()
    results["publication_figures"] = "SUCCESS"
except Exception as e:
    results["publication_figures"] = f"FAILED: {e}"
    traceback.print_exc()

# ─── 4. Summary Dashboard ───
print("\n" + "="*60)
print("4. Summary Dashboard")
print("="*60)
try:
    import scripts.analysis.generate_summary_dashboard as dash_mod
    importlib.reload(dash_mod)
    dash_mod.OUT = str(TMP_FIG / "project_summary_dashboard.png")
    # The script runs at import-time; we need to re-execute
    # Check if it has a main() or runs inline
    # It runs inline, so we need to exec it with patched OUT
    # Let's just exec the file with modified globals
    dash_code = (PROJECT / "scripts" / "analysis" / "generate_summary_dashboard.py").read_text()
    dash_code = dash_code.replace(
        'OUT     = os.path.join(PROJECT, "results", "figures", "project_summary_dashboard.png")',
        f'OUT     = "{TMP_FIG / "project_summary_dashboard.png"}"'
    )
    exec(compile(dash_code, "generate_summary_dashboard.py", "exec"), {"__name__": "__main__", "__file__": str(PROJECT / "scripts" / "analysis" / "generate_summary_dashboard.py")})
    results["summary_dashboard"] = "SUCCESS"
except Exception as e:
    results["summary_dashboard"] = f"FAILED: {e}"
    traceback.print_exc()

# ─── 5. Precinct Demand Visualizations ───
print("\n" + "="*60)
print("5. Precinct Demand Visualizations")
print("="*60)
try:
    import scripts.analysis.generate_precinct_demand_visualizations as pct_mod
    importlib.reload(pct_mod)
    pct_mod.FIGURES_DIR = TMP_FIG
    pct_mod.main()
    results["precinct_demand"] = "SUCCESS"
except Exception as e:
    results["precinct_demand"] = f"FAILED: {e}"
    traceback.print_exc()

# ─── Summary ───
print("\n" + "="*60)
print("REGENERATION SUMMARY")
print("="*60)
for name, status in results.items():
    icon = "✅" if status == "SUCCESS" else "❌"
    print(f"  {icon} {name}: {status}")
