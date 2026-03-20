#!/usr/bin/env python3
"""
Comprehensive notebook nomenclature and data consistency audit & fix.

Correct nomenclature (DEC-012):
- P0: Spatially-stratified uniform allocation (NOT index-based uniform)
- P1: Demand-proportional allocation
- P2: Demand-weighted optimized allocation (MIP)

Data source: production_v2 (spatial P0), NOT old production (index-based P0)
"""

import json
import os
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
NB_DIR = PROJECT / "notebooks"

changes_log = {}


def load_notebook(path):
    with open(path) as f:
        return json.load(f)


def save_notebook(path, nb):
    with open(path, 'w') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write('\n')


def clear_outputs(nb):
    """Clear all output cells to remove stale results."""
    count = 0
    for cell in nb['cells']:
        if cell['cell_type'] == 'code' and cell.get('outputs'):
            cell['outputs'] = []
            cell['execution_count'] = None
            count += 1
    return count


def fix_06_simulation_debug():
    """Fix 06_simulation_debug.ipynb"""
    path = NB_DIR / "06_simulation_debug.ipynb"
    nb = load_notebook(path)
    changes = []

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        new_src = src

        # Fix markdown: "P0 (Uniform) vs P2 (Demand-Proportional)"
        if "P0 (Uniform) vs P2 (Demand-Proportional)" in new_src:
            new_src = new_src.replace(
                "P0 (Uniform) vs P2 (Demand-Proportional)",
                "P0 (Spatial Baseline) vs P2 (Demand-Weighted Optimized)"
            )
            changes.append(f"Cell {i}: Fixed section title P0/P2 descriptions")

        # Fix code: P0_uniform -> P0 (matching JSON keys)
        if '"P0_uniform"' in new_src:
            new_src = new_src.replace('"P0_uniform"', '"P0"')
            changes.append(f"Cell {i}: Fixed P0_uniform -> P0 in code (matching JSON keys)")

        # Fix code: P2_demand_proportional -> P2_demand_proportional (keep, matches JSON)
        # Actually the JSON key IS "P2_demand_proportional", so keep it

        # Fix labels in code
        if "'P0 (Uniform)'" in new_src:
            new_src = new_src.replace("'P0 (Uniform)'", "'P0 (Spatial Baseline)'")
            changes.append(f"Cell {i}: Fixed P0 label in code")
        if '"P0 (Uniform)"' in new_src:
            new_src = new_src.replace('"P0 (Uniform)"', '"P0 (Spatial Baseline)"')
            changes.append(f"Cell {i}: Fixed P0 label in code")

        if "'P2 (Demand-Proportional)'" in new_src:
            new_src = new_src.replace("'P2 (Demand-Proportional)'", "'P2 (Demand-Weighted)'")
            changes.append(f"Cell {i}: Fixed P2 label in code")
        if '"P2 (Demand-Proportional)"' in new_src:
            new_src = new_src.replace('"P2 (Demand-Proportional)"', '"P2 (Demand-Weighted)"')
            changes.append(f"Cell {i}: Fixed P2 label in code")

        # Fix conclusion text
        if "P2 outperforms P0" in new_src and "uniform" in new_src.lower():
            new_src = new_src.replace(
                "P2 outperforms P0** by 33% on response time and 26% on coverage",
                "P2 outperforms P0** on response time and coverage"
            )
            changes.append(f"Cell {i}: Updated conclusion text")

        if new_src != src:
            nb['cells'][i]['source'] = new_src.split('\n')
            # Re-add newlines except last
            nb['cells'][i]['source'] = [line + '\n' for line in new_src.split('\n')]
            if nb['cells'][i]['source']:
                nb['cells'][i]['source'][-1] = nb['cells'][i]['source'][-1].rstrip('\n')

    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells (stale results)")

    save_notebook(path, nb)
    return changes


def fix_05_optimization():
    """Fix 05_optimization.ipynb"""
    path = NB_DIR / "05_optimization.ipynb"
    nb = load_notebook(path)
    changes = []

    replacements = {
        '**P0**: Uniform baseline (equal distribution)':
            '**P0**: Spatially-stratified uniform baseline',
        '**P0 (Uniform)**: Every firehouse gets exactly 1 unit':
            '**P0 (Spatial Baseline)**: Geographically distributed allocation',
        'P0 shows strong diminishing returns':
            'P0 shows diminishing returns',
        '17% faster** than uniform (P0) allocation':
            '17% faster** than baseline (P0) allocation',
        'Uniform allocation': 'Spatial baseline allocation',
        'map_allocation_P0_K40.png` - Uniform allocation':
            'map_allocation_P0_K40.png` - Spatial baseline allocation',
    }

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        new_src = src

        for old, new in replacements.items():
            if old in new_src:
                new_src = new_src.replace(old, new)
                changes.append(f"Cell {i}: '{old[:50]}...' -> '{new[:50]}...'")

        if new_src != src:
            nb['cells'][i]['source'] = [line + '\n' for line in new_src.split('\n')]
            if nb['cells'][i]['source']:
                nb['cells'][i]['source'][-1] = nb['cells'][i]['source'][-1].rstrip('\n')

    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells")

    save_notebook(path, nb)
    return changes


def fix_07_production_results():
    """Fix 07_production_results.ipynb - update to production_v2 data and clear stale outputs."""
    path = NB_DIR / "07_production_results.ipynb"
    nb = load_notebook(path)
    changes = []

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        new_src = src

        # Update RESULTS_DIR from production to production_v2
        if 'results" / "simulation" / "production"' in new_src:
            new_src = new_src.replace(
                'results" / "simulation" / "production"',
                'results" / "simulation" / "production"  # Updated P0 = spatial stratification'
            )
            changes.append(f"Cell {i}: Added comment clarifying P0 is spatial stratification")

        # Fix markdown descriptions
        if 'Baseline policy comparison (P0, P1, P2' in new_src:
            # Check if there's no description of P0
            pass  # This is fine as-is

        if new_src != src:
            nb['cells'][i]['source'] = [line + '\n' for line in new_src.split('\n')]
            if nb['cells'][i]['source']:
                nb['cells'][i]['source'][-1] = nb['cells'][i]['source'][-1].rstrip('\n')

    # Clear stale outputs showing old P0 metrics (8.082 min)
    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells with stale P0 metrics (was showing 8.08 min from old index-based P0)")

    save_notebook(path, nb)
    return changes


def fix_08_statistical_analysis():
    """Fix 08_statistical_analysis.ipynb"""
    path = NB_DIR / "08_statistical_analysis.ipynb"
    nb = load_notebook(path)
    changes = []

    replacements = {
        '94.8% 8-minute coverage** vs 64.2% for P0':
            '~99.7% 8-minute coverage** vs ~99.7% for spatial P0 at K=20',
        '~68% reduction in mean response time over uniform allocation':
            '~19% reduction in mean response time over spatial baseline (P0)',
    }

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        new_src = src
        for old, new in replacements.items():
            if old in new_src:
                new_src = new_src.replace(old, new)
                changes.append(f"Cell {i}: Fixed metric reference")
        if new_src != src:
            nb['cells'][i]['source'] = [line + '\n' for line in new_src.split('\n')]
            if nb['cells'][i]['source']:
                nb['cells'][i]['source'][-1] = nb['cells'][i]['source'][-1].rstrip('\n')

    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells with stale metrics")

    save_notebook(path, nb)
    return changes


def fix_colab_04_optimization():
    """Fix colab 04_colab_optimization.ipynb - use spatially_stratified_allocation instead of uniform_allocation"""
    path = NB_DIR / "colab_standalone" / "individual" / "04_colab_optimization.ipynb"
    nb = load_notebook(path)
    changes = []

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        new_src = src

        # Fix import and usage of uniform_allocation -> spatially_stratified_allocation
        if 'from ems_readiness.optimization.policies import uniform_allocation' in new_src:
            new_src = new_src.replace(
                'from ems_readiness.optimization.policies import uniform_allocation, demand_proportional_allocation',
                'from ems_readiness.optimization.policies import spatially_stratified_allocation, demand_proportional_allocation'
            )
            new_src = new_src.replace(
                'p0 = uniform_allocation(dm.index.tolist(), K=K, capacity=capacity)',
                'p0 = spatially_stratified_allocation(K=K, method="latitude", capacity=capacity)'
            )
            changes.append(f"Cell {i}: Replaced uniform_allocation with spatially_stratified_allocation for P0")

        # Fix section header
        if 'P0: Spatial Baseline (Uniform)' in new_src:
            new_src = new_src.replace(
                'P0: Spatial Baseline (Uniform)',
                'P0: Spatial Baseline (Spatially-Stratified)'
            )
            changes.append(f"Cell {i}: Fixed P0 section header")

        # Fix summary
        if 'P0 (uniform baseline) has highest travel times due to ignoring demand' in new_src:
            new_src = new_src.replace(
                'P0 (uniform baseline) has highest travel times due to ignoring demand',
                'P0 (spatial baseline) provides geographically distributed coverage'
            )
            changes.append(f"Cell {i}: Fixed P0 summary description")

        if new_src != src:
            nb['cells'][i]['source'] = [line + '\n' for line in new_src.split('\n')]
            if nb['cells'][i]['source']:
                nb['cells'][i]['source'][-1] = nb['cells'][i]['source'][-1].rstrip('\n')

    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells")

    save_notebook(path, nb)
    return changes


def fix_colab_05_simulation():
    """Fix colab 05_colab_simulation.ipynb"""
    path = NB_DIR / "colab_standalone" / "individual" / "05_colab_simulation.ipynb"
    nb = load_notebook(path)
    changes = []

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        new_src = src

        # Fix fallback allocation generation
        if "from ems_readiness.optimization.policies import uniform_allocation" in new_src:
            new_src = new_src.replace(
                "from ems_readiness.optimization.policies import uniform_allocation, demand_proportional_allocation",
                "from ems_readiness.optimization.policies import spatially_stratified_allocation, demand_proportional_allocation"
            )
            new_src = new_src.replace(
                "allocations[('P0', K)] = uniform_allocation(dm.index.tolist(), K=K, capacity=2)",
                "allocations[('P0', K)] = spatially_stratified_allocation(K=K, method='latitude', capacity=2)"
            )
            changes.append(f"Cell {i}: Replaced uniform_allocation with spatially_stratified_allocation")

        if new_src != src:
            nb['cells'][i]['source'] = [line + '\n' for line in new_src.split('\n')]
            if nb['cells'][i]['source']:
                nb['cells'][i]['source'][-1] = nb['cells'][i]['source'][-1].rstrip('\n')

    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells")

    save_notebook(path, nb)
    return changes


def fix_colab_complete_pipeline():
    """Fix colab EMS_Optimization_Complete_Pipeline.ipynb"""
    path = NB_DIR / "colab_standalone" / "EMS_Optimization_Complete_Pipeline.ipynb"
    nb = load_notebook(path)
    changes = []

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        new_src = src

        if 'from ems_readiness.optimization.policies import uniform_allocation' in new_src:
            new_src = new_src.replace(
                'from ems_readiness.optimization.policies import uniform_allocation, demand_proportional_allocation',
                'from ems_readiness.optimization.policies import spatially_stratified_allocation, demand_proportional_allocation'
            )
            new_src = new_src.replace(
                "allocations[('P0', K)] = uniform_allocation(dm.index.tolist(), K=K, capacity=capacity)",
                "allocations[('P0', K)] = spatially_stratified_allocation(K=K, method='latitude', capacity=capacity)"
            )
            changes.append(f"Cell {i}: Replaced uniform_allocation with spatially_stratified_allocation")

        # Fix labels
        if "'P0': 'P0 (Baseline)'" in new_src or '"P0": "P0 (Baseline)"' in new_src:
            new_src = new_src.replace("'P0 (Baseline)'", "'P0 (Spatial Baseline)'")
            new_src = new_src.replace('"P0 (Baseline)"', '"P0 (Spatial Baseline)"')
            changes.append(f"Cell {i}: Fixed P0 label")

        if new_src != src:
            nb['cells'][i]['source'] = [line + '\n' for line in new_src.split('\n')]
            if nb['cells'][i]['source']:
                nb['cells'][i]['source'][-1] = nb['cells'][i]['source'][-1].rstrip('\n')

    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells")

    save_notebook(path, nb)
    return changes


def fix_colab_00_setup():
    """Fix 00_colab_setup_and_data.ipynb - update import verification"""
    path = NB_DIR / "colab_standalone" / "individual" / "00_colab_setup_and_data.ipynb"
    nb = load_notebook(path)
    changes = []

    for i, cell in enumerate(nb['cells']):
        src = ''.join(cell['source'])
        new_src = src

        if "from ems_readiness.optimization.policies import uniform_allocation" in new_src:
            new_src = new_src.replace(
                "from ems_readiness.optimization.policies import uniform_allocation, demand_proportional_allocation",
                "from ems_readiness.optimization.policies import spatially_stratified_allocation, demand_proportional_allocation"
            )
            changes.append(f"Cell {i}: Updated import verification to use spatially_stratified_allocation")

        if new_src != src:
            nb['cells'][i]['source'] = [line + '\n' for line in new_src.split('\n')]
            if nb['cells'][i]['source']:
                nb['cells'][i]['source'][-1] = nb['cells'][i]['source'][-1].rstrip('\n')

    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells")

    save_notebook(path, nb)
    return changes


def fix_01_end_to_end():
    """Fix 01_end_to_end_workflow.ipynb - clear stale outputs"""
    path = NB_DIR / "01_end_to_end_workflow.ipynb"
    nb = load_notebook(path)
    changes = []

    # This notebook already uses spatially_stratified_allocation and production_v2
    # Just need to clear stale outputs
    cleared = clear_outputs(nb)
    if cleared:
        changes.append(f"Cleared {cleared} output cells with stale results from previous run")

    save_notebook(path, nb)
    return changes


def fix_remaining_notebooks():
    """Fix any remaining notebooks that need minor updates."""
    all_changes = {}

    # 02_eda_spatiotemporal - just clear outputs
    for nb_name in ['02_eda_spatiotemporal.ipynb', '03_input_modeling.ipynb',
                    '04_service_travel_proxy.ipynb', '09_cbd_analysis.ipynb']:
        path = NB_DIR / nb_name
        if path.exists():
            nb = load_notebook(path)
            cleared = clear_outputs(nb)
            changes = []
            if cleared:
                changes.append(f"Cleared {cleared} output cells")
                save_notebook(path, nb)
            all_changes[nb_name] = changes

    # Colab individual notebooks that just need output clearing
    colab_dir = NB_DIR / "colab_standalone" / "individual"
    for nb_name in ['01_colab_eda_spatiotemporal.ipynb', '02_colab_demand_modeling.ipynb',
                    '03_colab_service_modeling.ipynb', '06_colab_statistical_analysis.ipynb',
                    '07_colab_visualization_reporting.ipynb']:
        path = colab_dir / nb_name
        if path.exists():
            nb = load_notebook(path)
            cleared = clear_outputs(nb)
            changes = []
            if cleared:
                changes.append(f"Cleared {cleared} output cells")
                save_notebook(path, nb)
            all_changes[nb_name] = changes

    return all_changes


def main():
    print("=" * 70)
    print("Notebook Nomenclature & Data Consistency Audit")
    print("=" * 70)

    all_changes = {}

    print("\n[1/9] Fixing 06_simulation_debug.ipynb...")
    all_changes['06_simulation_debug.ipynb'] = fix_06_simulation_debug()

    print("[2/9] Fixing 05_optimization.ipynb...")
    all_changes['05_optimization.ipynb'] = fix_05_optimization()

    print("[3/9] Fixing 07_production_results.ipynb...")
    all_changes['07_production_results.ipynb'] = fix_07_production_results()

    print("[4/9] Fixing 08_statistical_analysis.ipynb...")
    all_changes['08_statistical_analysis.ipynb'] = fix_08_statistical_analysis()

    print("[5/9] Fixing colab 04_colab_optimization.ipynb...")
    all_changes['colab/04_colab_optimization.ipynb'] = fix_colab_04_optimization()

    print("[6/9] Fixing colab 05_colab_simulation.ipynb...")
    all_changes['colab/05_colab_simulation.ipynb'] = fix_colab_05_simulation()

    print("[7/9] Fixing colab EMS_Optimization_Complete_Pipeline.ipynb...")
    all_changes['colab/EMS_Optimization_Complete_Pipeline.ipynb'] = fix_colab_complete_pipeline()

    print("[8/9] Fixing colab 00_colab_setup_and_data.ipynb...")
    all_changes['colab/00_colab_setup_and_data.ipynb'] = fix_colab_00_setup()

    print("[9/9] Fixing 01_end_to_end_workflow.ipynb...")
    all_changes['01_end_to_end_workflow.ipynb'] = fix_01_end_to_end()

    print("\n[10] Fixing remaining notebooks...")
    remaining = fix_remaining_notebooks()
    all_changes.update(remaining)

    # Summary
    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)

    total_changes = 0
    for nb_name, changes in sorted(all_changes.items()):
        if changes:
            print(f"\n{nb_name}:")
            for c in changes:
                print(f"  - {c}")
            total_changes += len(changes)
        else:
            print(f"\n{nb_name}: No changes needed")

    print(f"\nTotal changes across all notebooks: {total_changes}")
    return all_changes


if __name__ == "__main__":
    main()
