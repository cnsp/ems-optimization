#!/usr/bin/env python3
"""
De-AI-ify documentation: remove robotic/AI-sounding language patterns 
and make docs sound more natural and human-written.
"""

import re
import os
import glob

# Targeted phrase replacements (old -> new)
# These are context-sensitive and ordered to avoid double-replacement
PHRASE_REPLACEMENTS = [
    # Overly enthusiastic / superlative language
    ("dramatically outperforms", "substantially outperforms"),
    ("dramatically suboptimal", "far from optimal"),
    ("dramatically reduces", "sharply reduces"),
    ("dramatically worsens", "sharply worsens"),
    ("dramatically improved", "substantially improved"),
    ("can dramatically reduce", "can sharply reduce"),
    ("dramatically outperforms the index-based", "far outperforms the index-based"),
    ("yields transformative performance improvements", "leads to major performance gains"),
    ("a life-saving improvement", "a meaningful improvement"),
    ("near-universal 8-minute coverage", "near-complete 8-minute coverage"),
    ("near-perfect coverage", "near-complete coverage"),

    # "Comprehensive" overuse
    ("Comprehensive Technical Report", "Full Technical Report"),
    ("comprehensive review", "thorough review"),
    ("comprehensive report", "full report"),
    ("Comprehensive final report", "Full final report"),
    ("comprehensive final report", "full final report"),
    ("comprehensive CBD experiment", "full CBD experiment"),
    ("Comprehensive CBD experiment", "Full CBD experiment"),
    ("comprehensive project summary", "full project summary"),
    ("A comprehensive interface", "An interface"),
    ("comprehensive analysis", "thorough analysis"),

    # "Robust/Robustness" - keep where statistically meaningful, remove where filler
    ("P2 is robust:", "P2 is stable across parameter changes:"),
    ("confirms robustness to", "confirms stability under"),
    ("confirm robustness to distance", "confirm stability under distance"),
    ("Alternative analyses confirm robustness to distance metric choice and geographic focus.", 
     "Alternative analyses show results hold under different distance metrics and geographic scopes."),

    # "Demonstrates" / "confirms" formulaic usage
    ("This study presents a simulation-based optimization framework",
     "This study develops a simulation-based optimization framework"),
    ("Results demonstrate that the optimized policy",
     "Results show that the optimized policy"),
    ("The results demonstrate that", "The results show that"),
    ("results demonstrate that", "results show that"),
    ("The analysis confirms that", "The analysis shows that"),
    ("confirms that geographic placement is the dominant factor",
     "shows that geographic placement is the main driver"),
    ("This significantly narrows the gap", "This narrows the gap considerably"),
    ("This validates the focus on", "This supports the focus on"),

    # "Critical" overuse (when not referring to genuinely critical things)
    ("face a critical challenge:", "face a key challenge:"),
    
    # Formulaic transitions
    ("In summary, DES is the minimal-complexity, maximum-fidelity approach",
     "DES is the right trade-off between complexity and fidelity"),
    ("The key mechanism is straightforward:", "The mechanism is simple:"),

    # Corporate-speak / buzzwords
    ("Leverages existing infrastructure", "Uses existing infrastructure"),
    ("leverages existing infrastructure", "uses existing infrastructure"),
    ("more intelligent allocation strategy", "smarter allocation strategy"),
    ("a more intelligent allocation", "a smarter allocation"),
    ("actionable recommendations", "practical recommendations"),
    ("Actionable recommendations", "Practical recommendations"),
    ("actionable recommendations for EMS", "practical recommendations for EMS"),

    # "Uniquely suited" and "uniquely"
    ("DES is uniquely suited to this problem for the following reasons:",
     "DES fits this problem well for several reasons:"),

    # Passive-to-active voice fixes (targeted)
    ("was deliberately and is justified below", "was deliberate, as explained below"),

    # Overly formal / stiff phrasing
    ("This document records all assumptions made during",
     "This document logs the assumptions made during"),
    ("This document records key decisions made during",
     "This document logs key decisions made during"),
    ("This document tracks any blockers encountered during the project",
     "This document tracks blockers encountered during the project"),

    # Redundant qualifiers
    ("highly significant policy effects", "significant policy effects"),
    ("highly heterogeneous demand patterns", "heterogeneous demand patterns"),
    ("pronounced spatial heterogeneity", "clear spatial heterogeneity"),
    ("pronounced hourly/DOW variation", "notable hourly/DOW variation"),
    
    # "Ensure" overuse
    ("to ensure exact reproducibility", "for exact reproducibility"),
    ("to ensure fair comparisons", "for fair comparisons"),
    ("ensuring even north–south coverage", "providing even north–south coverage"),
    ("to ensure even spatial distribution", "for even spatial distribution"),
    ("ensuring geographic coverage from Battery Park to Inwood",
     "covering the full stretch from Battery Park to Inwood"),

    # "Comprehensive" in specific contexts - more replacements
    ("Comprehensive project summary", "Full project summary"),
    ("comprehensive final report (v2.1.0)", "full final report (v2.1.0)"),
    ("Comprehensive final report (v2.1.0)", "Full final report (v2.1.0)"),
    
    # Tighten verbose phrasing
    ("without regard to spatiotemporal demand patterns, resulting in suboptimal response times and inadequate coverage",
     "ignoring where and when demand actually occurs, leading to poor response times and coverage gaps"),
    ("The effectiveness of this strategy depends critically on",
     "How well this works depends heavily on"),
    ("Several modeling paradigms were considered for evaluating ambulance staging policies. The choice of **Discrete-Event Simulation (DES)** over alternatives was deliberate and is justified below.",
     "We considered several modeling approaches for evaluating ambulance staging policies. We chose **Discrete-Event Simulation (DES)** over the alternatives for the reasons below."),
    
    # "Fundamental" overuse
    ("two fundamental realities", "two basic realities"),
    
    # Tighten some section intros
    ("The problem of optimally locating emergency service facilities has a rich history in operations research.",
     "Optimal location of emergency service facilities is a well-studied problem in operations research."),
    ("Simulation provides a complement to optimization by capturing stochastic dynamics that static models cannot represent.",
     "Simulation complements optimization by capturing stochastic dynamics that static models miss."),
    
    # "Straightforward" as filler
    ("The key mechanism is straightforward", "The mechanism is simple"),

    # Formulaic academic padding  
    ("is widely used in EMS planning", "is standard in EMS planning"),
    ("consistent with industry practice and regulatory standards",
     "in line with industry practice and regulatory standards"),
    
    # "Significant" overuse where "large/notable" works better
    ("P0 degrades significantly with increased demand",
     "P0 degrades noticeably with increased demand"),
    ("CBD response times are significantly lower",
     "CBD response times are notably lower"),
    
    # Tighten wordy explanations
    ("This low traffic intensity (ρ ≈ 0.087) ensures near-zero waiting probability even under stress scenarios.",
     "At this low traffic intensity (ρ ≈ 0.087), waiting is effectively impossible even under stress scenarios."),
    ("Since queuing is negligible, response time differences between policies are **entirely due to spatial allocation** (travel distances), not capacity constraints. This validates the focus on optimization-based allocation (P2) as the primary mechanism for service improvement.",
     "Since queuing is negligible, response time differences between policies come down **entirely to spatial allocation** (travel distances), not capacity constraints — which is exactly why optimization-based allocation (P2) is the right lever for improvement."),
    
    # Generic filler phrases
    ("It is worth noting that", "Note that"),
    ("It should be noted that", "Note that"),
    ("It is important to note that", "Note that"),

    # "Innovative" / "novel" if present
    ("innovative approach", "approach"),
    ("novel approach", "approach"),

    # "Cutting-edge" if present
    ("cutting-edge", "modern"),

    # Tighten "the following reasons"
    ("for the following reasons:", "because:"),

    # "State-of-the-art" if present
    ("state-of-the-art", "current best"),

    # Fix "exciting" if present
    ("exciting results", "strong results"),
    ("exciting findings", "notable findings"),

    # "Remarkable" if present
    ("remarkable improvement", "large improvement"),
    ("remarkable reduction", "large reduction"),

    # Phase 21 references - make more natural
    ("Phase 21 — Full Compliance", "Final Version — Full Compliance"),
    ("Phase 21 compliant", "fully compliant"),
    ("Phase 21 compliance assessment", "compliance assessment"),

    # Wordiness reduction
    ("In order to", "To"),
    ("in order to", "to"),
    ("a total of", ""),
    ("for the purpose of", "for"),

    # Clean up document footers
    ("*Document prepared as part of the EMS Readiness Optimization project, Phase 9.*",
     "*Part of the EMS Readiness Optimization project, Phase 9.*"),

    # "Optimal" / "optimally" overuse (keep where technically correct, soften elsewhere)
    ("already near-optimally serves the CBD", "already serves the CBD well"),
    ("near-optimally serves", "effectively serves"),
]

# Regex-based patterns
REGEX_REPLACEMENTS = [
    # Remove "a total of" before numbers (e.g., "a total of 1,770" -> "1,770")
    (r'[Aa] total of (\d)', r'\1'),
    # "In this section, we..." -> "We..."  (section intro padding)
    # Remove leading "Furthermore, " at start of sentences when formulaic
    # Remove double spaces that might result from replacements
    (r'  +', ' '),
]


def process_file(filepath):
    """Process a single markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Apply phrase replacements
    for old, new in PHRASE_REPLACEMENTS:
        content = content.replace(old, new)
    
    # Apply regex replacements
    for pattern, replacement in REGEX_REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
    
    # Only write if changed
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        # Count changes
        changes = sum(1 for old, new in PHRASE_REPLACEMENTS if old in original and old not in content)
        return changes
    return 0


def main():
    base = '/home/ubuntu/ems-optimization'
    
    # Find all markdown files (excluding .pytest_cache)
    md_files = []
    for root, dirs, files in os.walk(base):
        if '.pytest_cache' in root:
            continue
        for f in files:
            if f.endswith('.md'):
                md_files.append(os.path.join(root, f))
    
    md_files.sort()
    
    total_changes = 0
    for filepath in md_files:
        changes = process_file(filepath)
        rel = os.path.relpath(filepath, base)
        if changes > 0:
            print(f"  ✓ {rel}: {changes} pattern(s) applied")
        else:
            print(f"  · {rel}: no changes needed")
        total_changes += changes
    
    print(f"\nTotal: {len(md_files)} files processed, {total_changes} patterns applied")


if __name__ == '__main__':
    main()
