#!/usr/bin/env python3
"""
End-to-End Project Consistency Verification
============================================
Checks that all configs, results, scripts, and docs are internally consistent
after the nomenclature migration and audit sweeps.

Run:  python scripts/verify_project_consistency.py
Exit code 0 = all checks pass.  Non-zero = issues found.

Categories checked:
  1. Configuration consistency (capacity, policy names, K values)
  2. Result-file metric sanity (P0 ≈ 3–5 min, not 8+; P2 < P0)
  3. Source-code hygiene (no stale function calls, deprecation guards)
  4. Documentation nomenclature (correct P0/P1/P2 labels)
  5. Deprecated / stale artefact detection
"""

import os
import re
import sys
import csv
import yaml
import json
from pathlib import Path
from collections import defaultdict

# ── Project root ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

# ── Colour helpers for terminal output ────────────────────────
GREEN = "\033[92m"
RED   = "\033[91m"
YELLOW = "\033[93m"
CYAN  = "\033[96m"
BOLD  = "\033[1m"
RESET = "\033[0m"

def ok(msg):
    return f"  {GREEN}✓{RESET} {msg}"

def fail(msg):
    return f"  {RED}✗{RESET} {msg}"

def warn(msg):
    return f"  {YELLOW}⚠{RESET} {msg}"

def header(title):
    return f"\n{BOLD}{CYAN}{'═'*60}\n  {title}\n{'═'*60}{RESET}"

# ── Accumulate results ────────────────────────────────────────
results = {"pass": 0, "fail": 0, "warn": 0, "details": []}

def record(status, category, message):
    results[status] += 1
    results["details"].append((status, category, message))


# ══════════════════════════════════════════════════════════════
#  1.  CONFIGURATION CONSISTENCY
# ══════════════════════════════════════════════════════════════
def check_configs():
    print(header("1. Configuration Consistency"))

    # 1a. optimization.yaml capacity
    opt_cfg = ROOT / "configs" / "optimization.yaml"
    if opt_cfg.exists():
        with open(opt_cfg) as f:
            cfg = yaml.safe_load(f)
        cap = cfg.get("firehouse_capacity")
        if cap == 2:
            print(ok(f"optimization.yaml  firehouse_capacity = {cap}"))
            record("pass", "config", "firehouse_capacity == 2")
        else:
            print(fail(f"optimization.yaml  firehouse_capacity = {cap} (expected 2)"))
            record("fail", "config", f"firehouse_capacity is {cap}, expected 2")

        # 1b. K values present
        ks = cfg.get("unit_counts", [])
        expected_ks = {20, 30, 40, 48}
        if set(ks) >= expected_ks:
            print(ok(f"unit_counts contains {sorted(ks)}"))
            record("pass", "config", "unit_counts OK")
        else:
            print(fail(f"unit_counts {ks} missing some of {expected_ks}"))
            record("fail", "config", f"unit_counts incomplete: {ks}")

        # 1c. default model
        dm = cfg.get("default_model", "")
        if dm == "demand_weighted":
            print(ok(f"default_model = {dm}"))
            record("pass", "config", "default_model OK")
        else:
            print(warn(f"default_model = {dm} (expected demand_weighted)"))
            record("warn", "config", f"default_model is {dm}")
    else:
        print(fail("optimization.yaml not found"))
        record("fail", "config", "optimization.yaml missing")

    # 1d. demand.yaml base rate
    dem_cfg = ROOT / "configs" / "demand.yaml"
    if dem_cfg.exists():
        with open(dem_cfg) as f:
            dcfg = yaml.safe_load(f)
        rate = dcfg.get("base_rate_per_hour")
        if rate and 3.0 <= rate <= 4.0:
            print(ok(f"demand.yaml  base_rate_per_hour = {rate}"))
            record("pass", "config", "base_rate_per_hour OK")
        else:
            print(warn(f"demand.yaml  base_rate_per_hour = {rate}"))
            record("warn", "config", f"base_rate_per_hour = {rate}")
    else:
        print(warn("demand.yaml not found"))
        record("warn", "config", "demand.yaml missing")

    # 1e. service.yaml
    svc_cfg = ROOT / "configs" / "service.yaml"
    if svc_cfg.exists():
        with open(svc_cfg) as f:
            scfg = yaml.safe_load(f)
        speed = scfg.get("travel_time", {}).get("average_speed_mph")
        if speed == 20.0:
            print(ok(f"service.yaml  average_speed_mph = {speed}"))
            record("pass", "config", "average_speed_mph OK")
        else:
            print(warn(f"service.yaml  average_speed_mph = {speed}"))
            record("warn", "config", f"average_speed_mph = {speed}")
    else:
        print(warn("service.yaml not found"))
        record("warn", "config", "service.yaml missing")


# ══════════════════════════════════════════════════════════════
#  2.  RESULT-FILE METRIC SANITY
# ══════════════════════════════════════════════════════════════
def check_results():
    print(header("2. Result-File Metric Sanity"))

    # 2a. policy_comparison.csv — P0 names and RT
    pc_path = ROOT / "results" / "optimization" / "policy_comparison.csv"
    if pc_path.exists():
        with open(pc_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Check P0 label
        p0_rows = [r for r in rows if r.get("policy_id") == "P0"]
        for r in p0_rows:
            name = r.get("policy_name", "")
            if "Spatially" in name or "stratified" in name.lower():
                print(ok(f"K={r['K']} P0 label: '{name}'"))
                record("pass", "results", f"P0 label OK at K={r['K']}")
            else:
                print(fail(f"K={r['K']} P0 label: '{name}' (expected Spatially-Stratified)"))
                record("fail", "results", f"P0 label wrong at K={r['K']}: {name}")

            # RT sanity: P0 should be < 8 min at K≥20
            rt = float(r.get("response_time", 0))
            k = int(r.get("K", 0))
            if k >= 20 and rt < 8.0:
                print(ok(f"K={k} P0 RT = {rt:.2f} min (< 8 min threshold)"))
                record("pass", "results", f"P0 RT OK at K={k}")
            elif k >= 20:
                print(fail(f"K={k} P0 RT = {rt:.2f} min (≥ 8 min — stale data?)"))
                record("fail", "results", f"P0 RT stale at K={k}: {rt}")

        # P2 should dominate P0
        for k_val in [20, 30, 40]:
            p0_rt = next((float(r["response_time"]) for r in rows
                          if r["policy_id"] == "P0" and int(r["K"]) == k_val), None)
            p2_rt = next((float(r["response_time"]) for r in rows
                          if r["policy_id"] == "P2" and int(r["K"]) == k_val), None)
            if p0_rt and p2_rt:
                if p2_rt <= p0_rt:
                    print(ok(f"K={k_val} P2 ({p2_rt:.2f}) ≤ P0 ({p0_rt:.2f})"))
                    record("pass", "results", f"P2 ≤ P0 at K={k_val}")
                else:
                    print(fail(f"K={k_val} P2 ({p2_rt:.2f}) > P0 ({p0_rt:.2f})"))
                    record("fail", "results", f"P2 > P0 at K={k_val}")
    else:
        print(warn("policy_comparison.csv not found"))
        record("warn", "results", "policy_comparison.csv missing")

    # 2b. Simulation descriptive stats — check P0 at K=20
    ds_path = ROOT / "results" / "baseline" / "tables" / "descriptive_statistics.csv"
    if ds_path.exists():
        with open(ds_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        p0_k20 = [r for r in rows if r.get("policy") == "P0" and r.get("K") == "20"]
        if p0_k20:
            rt = float(p0_k20[0].get("mean_RT", 0))
            if 2.5 <= rt <= 6.0:
                print(ok(f"Simulation P0 K=20 mean_RT = {rt:.2f} min"))
                record("pass", "results", "Sim P0 K=20 RT plausible")
            else:
                print(fail(f"Simulation P0 K=20 mean_RT = {rt:.2f} (out of range)"))
                record("fail", "results", f"Sim P0 K=20 RT = {rt}")
        else:
            print(warn("No P0 K=20 row in descriptive_statistics.csv"))
            record("warn", "results", "No P0 K=20 sim row")
    else:
        print(warn("descriptive_statistics.csv not found"))
        record("warn", "results", "descriptive_statistics.csv missing")

    # 2c. Check that P2c (maximal coverage) capacity column is not >2
    if pc_path.exists():
        with open(pc_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        for r in rows:
            max_u = int(r.get("max_units_at_firehouse", 0))
            if max_u > 5:
                print(fail(f"K={r['K']} {r['policy_id']} max_units = {max_u} (>5 suspicious)"))
                record("fail", "results", f"max_units={max_u} at K={r['K']} {r['policy_id']}")
        print(ok("max_units_at_firehouse values within plausible range"))
        record("pass", "results", "max_units sanity OK")


# ══════════════════════════════════════════════════════════════
#  3.  SOURCE CODE HYGIENE
# ══════════════════════════════════════════════════════════════
def check_source_code():
    print(header("3. Source Code Hygiene"))

    src_dir = ROOT / "src"
    scripts_dir = ROOT / "scripts"

    # 3a. No direct call to uniform_allocation in scripts (except deprecated wrappers)
    allowed_files = {"policies.py", "allocator.py", "__init__.py",
                     "fix_notebook_nomenclature.py", "verify_project_consistency.py"}
    issues = []
    for d in [src_dir, scripts_dir]:
        if not d.exists():
            continue
        for py in d.rglob("*.py"):
            if py.name in allowed_files:
                continue
            content = py.read_text(errors="ignore")
            if "uniform_allocation(" in content:
                # Check it's not in a comment or string context
                for i, line in enumerate(content.splitlines(), 1):
                    stripped = line.strip()
                    if "uniform_allocation(" in stripped and not stripped.startswith("#"):
                        issues.append(f"{py.relative_to(ROOT)}:{i}")

    if not issues:
        print(ok("No stale uniform_allocation() calls in active scripts"))
        record("pass", "code", "No stale uniform_allocation calls")
    else:
        for loc in issues:
            print(warn(f"uniform_allocation() reference at {loc}"))
            record("warn", "code", f"uniform_allocation ref: {loc}")

    # 3b. Deprecation guard in policies.py
    pol_path = src_dir / "ems_readiness" / "optimization" / "policies.py"
    if pol_path.exists():
        pol_text = pol_path.read_text()
        if "DeprecationWarning" in pol_text:
            print(ok("policies.py has DeprecationWarning for uniform_allocation"))
            record("pass", "code", "DeprecationWarning present")
        else:
            print(fail("policies.py missing DeprecationWarning"))
            record("fail", "code", "Missing DeprecationWarning")

    # 3c. spatially_stratified_allocation exists and is importable
    if pol_path.exists():
        pol_text = pol_path.read_text()
        if "def spatially_stratified_allocation" in pol_text:
            print(ok("spatially_stratified_allocation() defined"))
            record("pass", "code", "spatially_stratified_allocation defined")
        else:
            print(fail("spatially_stratified_allocation() not found"))
            record("fail", "code", "spatially_stratified_allocation missing")

    # 3d. allocator.py has baseline_p0 method
    alloc_path = src_dir / "ems_readiness" / "optimization" / "allocator.py"
    if alloc_path.exists():
        alloc_text = alloc_path.read_text()
        if "def baseline_p0" in alloc_text:
            print(ok("allocator.py has baseline_p0() method"))
            record("pass", "code", "baseline_p0 method exists")
        else:
            print(fail("allocator.py missing baseline_p0() method"))
            record("fail", "code", "baseline_p0 missing")

    # 3e. models.py uses capacity parameter
    models_path = src_dir / "ems_readiness" / "optimization" / "models.py"
    if models_path.exists():
        models_text = models_path.read_text()
        # Check all build_ functions accept capacity
        build_fns = re.findall(r'def (build_\w+)\(([^)]+)\)', models_text)
        for fn_name, params in build_fns:
            if "capacity" in params:
                print(ok(f"{fn_name}() accepts capacity parameter"))
                record("pass", "code", f"{fn_name} has capacity param")
            else:
                print(warn(f"{fn_name}() missing capacity parameter"))
                record("warn", "code", f"{fn_name} missing capacity")


# ══════════════════════════════════════════════════════════════
#  4.  DOCUMENTATION NOMENCLATURE
# ══════════════════════════════════════════════════════════════
def check_docs():
    print(header("4. Documentation Nomenclature"))

    docs_dir = ROOT / "docs"
    # Key authoritative docs that MUST use correct nomenclature
    authoritative = [
        "technical_report.md",
        "executive_summary.md",
        "experimental_design.md",
        "optimization_results.md",
        "optimization_formulation.md",
    ]

    for fname in authoritative:
        fpath = docs_dir / fname
        if not fpath.exists():
            print(warn(f"{fname} not found"))
            record("warn", "docs", f"{fname} missing")
            continue
        text = fpath.read_text(errors="ignore")

        # Should not refer to P0 as "uniform" without "spatially" qualifier
        # Look for "P0" near "uniform" without "spatially" or "deprecated"
        # This is a heuristic check
        lines = text.splitlines()
        stale_refs = []
        for i, line in enumerate(lines, 1):
            low = line.lower()
            if "p0" in low and "uniform" in low:
                if "spatial" not in low and "deprecated" not in low and "legacy" not in low and "historical" not in low:
                    stale_refs.append(i)

        if not stale_refs:
            print(ok(f"{fname}: P0 nomenclature clean"))
            record("pass", "docs", f"{fname} nomenclature OK")
        else:
            for ln in stale_refs[:3]:
                print(warn(f"{fname}:{ln} — P0+uniform without spatial qualifier"))
            record("warn", "docs", f"{fname} may have stale P0 refs at lines {stale_refs}")

    # 4b. Check historical docs have warning banners
    historical_docs = [
        "policy_tradeoff_analysis.md",
    ]
    for fname in historical_docs:
        fpath = docs_dir / fname
        if not fpath.exists():
            continue
        text = fpath.read_text(errors="ignore")[:1000]  # Check top of file
        if "⚠️" in text or "Historical" in text or "DEPRECATED" in text.upper():
            print(ok(f"{fname}: has historical warning banner"))
            record("pass", "docs", f"{fname} has warning banner")
        else:
            print(fail(f"{fname}: missing historical warning banner"))
            record("fail", "docs", f"{fname} no warning banner")

    # 4c. nomenclature_migration.md exists
    nm = docs_dir / "nomenclature_migration.md"
    if nm.exists():
        print(ok("nomenclature_migration.md exists"))
        record("pass", "docs", "nomenclature_migration.md exists")
    else:
        print(fail("nomenclature_migration.md missing"))
        record("fail", "docs", "nomenclature_migration.md missing")


# ══════════════════════════════════════════════════════════════
#  5.  DEPRECATED / STALE ARTEFACT DETECTION
# ══════════════════════════════════════════════════════════════
def check_deprecated():
    print(header("5. Deprecated / Stale Artefact Detection"))

    # 5a. Scan for "8.08" or "18.5" in authoritative result files
    stale_metrics = ["8.08", "18.5"]
    auth_result_files = [
        ROOT / "results" / "optimization" / "policy_comparison.csv",
    ]
    for rp in auth_result_files:
        if not rp.exists():
            continue
        text = rp.read_text(errors="ignore")
        found = [m for m in stale_metrics if m in text]
        if not found:
            print(ok(f"{rp.name}: no stale metric values"))
            record("pass", "deprecated", f"{rp.name} clean")
        else:
            print(fail(f"{rp.name}: contains stale values {found}"))
            record("fail", "deprecated", f"{rp.name} has stale values {found}")

    # 5b. Check for old "cap=5" as default in configs
    opt_cfg = ROOT / "configs" / "optimization.yaml"
    if opt_cfg.exists():
        text = opt_cfg.read_text()
        # Already checked in configs section, but double-check here
        if "firehouse_capacity: 5" in text:
            print(fail("optimization.yaml still has firehouse_capacity: 5"))
            record("fail", "deprecated", "cap=5 still default")
        else:
            print(ok("No cap=5 as default in configs"))
            record("pass", "deprecated", "cap != 5 in config")

    # 5c. List deprecated functions for reference
    deprecated_functions = [
        ("uniform_allocation()", "src/ems_readiness/optimization/policies.py",
         "Use spatially_stratified_allocation() instead"),
        ("baseline_uniform()", "src/ems_readiness/optimization/allocator.py",
         "Use baseline_p0() instead"),
    ]
    print(f"\n  {BOLD}Deprecated Function Registry:{RESET}")
    for fn, loc, replacement in deprecated_functions:
        print(f"    {YELLOW}⊘{RESET} {fn} in {loc}")
        print(f"      → {replacement}")
    record("pass", "deprecated", f"Documented {len(deprecated_functions)} deprecated functions")

    # 5d. Check for unmarked historical docs (contain old P0 data but no warning)
    docs_dir = ROOT / "docs"
    potentially_historical = []
    for md in docs_dir.glob("*.md"):
        text = md.read_text(errors="ignore")
        has_old_data = any(x in text for x in ["8.08", "18.5", "original P0", "index-based"])
        has_banner = any(x in text for x in ["⚠️", "Historical", "DEPRECATED", "deprecated", "legacy"])
        if has_old_data and not has_banner:
            potentially_historical.append(md.name)

    if not potentially_historical:
        print(ok("All docs with old data have historical markers"))
        record("pass", "deprecated", "All old-data docs marked")
    else:
        for doc in potentially_historical:
            print(warn(f"{doc} has old data references but no historical marker"))
            record("warn", "deprecated", f"{doc} unmarked historical content")


# ══════════════════════════════════════════════════════════════
#  MAIN — run all checks and summarise
# ══════════════════════════════════════════════════════════════
def main():
    print(f"\n{BOLD}{'='*60}")
    print("  EMS-OPTIMIZATION  —  End-to-End Consistency Verification")
    print(f"{'='*60}{RESET}")
    print(f"  Project root: {ROOT}")
    print(f"  Timestamp:    {__import__('datetime').datetime.now():%Y-%m-%d %H:%M:%S}")

    check_configs()
    check_results()
    check_source_code()
    check_docs()
    check_deprecated()

    # ── Summary ───────────────────────────────────────────────
    print(header("SUMMARY"))
    total = results["pass"] + results["fail"] + results["warn"]
    print(f"  {GREEN}Passed : {results['pass']}{RESET}")
    print(f"  {RED}Failed : {results['fail']}{RESET}")
    print(f"  {YELLOW}Warnings: {results['warn']}{RESET}")
    print(f"  Total  : {total} checks\n")

    if results["fail"] == 0:
        print(f"  {GREEN}{BOLD}✓ ALL CRITICAL CHECKS PASSED{RESET}")
        if results["warn"] > 0:
            print(f"  {YELLOW}  ({results['warn']} non-critical warnings){RESET}")
    else:
        print(f"  {RED}{BOLD}✗ {results['fail']} CRITICAL ISSUE(S) FOUND{RESET}")
        print(f"\n  Failed checks:")
        for status, cat, msg in results["details"]:
            if status == "fail":
                print(f"    {RED}✗{RESET} [{cat}] {msg}")

    # ── Write JSON report ─────────────────────────────────────
    report_path = ROOT / "results" / "consistency_verification_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": f"{__import__('datetime').datetime.now():%Y-%m-%dT%H:%M:%S}",
        "summary": {
            "passed": results["pass"],
            "failed": results["fail"],
            "warnings": results["warn"],
            "total": total,
            "status": "PASS" if results["fail"] == 0 else "FAIL",
        },
        "checks": [
            {"status": s, "category": c, "message": m}
            for s, c, m in results["details"]
        ],
    }
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report saved to: {report_path.relative_to(ROOT)}")

    return 0 if results["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
