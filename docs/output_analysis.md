# Output Analysis – Statistical Methodology

## 1. Overview

This document specifies the statistical framework used to analyse results from the
EMS Readiness Optimization production experiments (Phase 5).  The analysis covers
**1 440 simulation replications** across four experiment sets and three allocation
policies.  All procedures follow publication standards for discrete-event simulation
output analysis (Law, 2015; Banks et al., 2010).

---

## 2. Primary Metrics

| Metric | Symbol | Definition |
|--------|--------|-----------|
| Mean Response Time | $\bar{R}$ | Average minutes from call arrival to unit arrival on scene |
| P90 Response Time | $R_{90}$ | 90th-percentile response time |
| 8-min Coverage | $C_8$ | Fraction of calls responded to within 8 minutes |
| Mean Utilization | $\bar{U}$ | Average fraction of time units are busy |

---

## 3. Hypothesis Testing Framework

### 3.1 Research Hypotheses

| ID | Hypothesis | Test |
|----|-----------|------|
| H1 | Allocation policy significantly affects mean response time | One-way ANOVA |
| H2 | Policy effect interacts with fleet size K | Two-way ANOVA (Policy × K) |
| H3 | Policy effect interacts with demand level | Two-way ANOVA (Policy × Demand) |
| H4 | Policy effect is robust to service-time variability | Two-way ANOVA (Policy × Service Time) |

### 3.2 Significance Level

All tests use **α = 0.05** (two-sided).  Family-wise error is controlled with
Bonferroni or Tukey adjustments where multiple comparisons are made.

---

## 4. ANOVA Design and Assumptions

### 4.1 One-Way ANOVA (Experiment 1)

- **Factor**: Policy ∈ {P0, P1, P2}
- **Response**: Mean response time per replication
- **Replications**: 30 per policy (Common Random Numbers)
- **Assumptions checked**:
  - Normality: Shapiro-Wilk test on residuals
  - Homogeneity of variance: Levene's test
  - Independence: ensured by CRN design

### 4.2 Two-Way ANOVA (Experiments 2–4)

| Experiment | Factor A | Factor B | Levels |
|------------|---------|---------|--------|
| Exp 2 | Policy (P0, P1, P2) | K (15, 20, 25, 30, 35, 40) | 3 × 6 = 18 cells |
| Exp 3 | Policy (P0, P1, P2) | Demand (0.5, 0.75, 1.0, 1.25, 1.5, 2.0) | 3 × 6 = 18 cells |
| Exp 4 | Policy (P0, P1, P2) | Service Time (20, 25, 30) | 3 × 3 = 9 cells |

- **Model**: $Y_{ijk} = \mu + \alpha_i + \beta_j + (\alpha\beta)_{ij} + \varepsilon_{ijk}$
- **Interaction term** $(\alpha\beta)_{ij}$ tests whether the policy advantage
  changes across factor levels.

### 4.3 Assumption Diagnostics

| Assumption | Test | Action if Violated |
|-----------|------|-------------------|
| Normality of residuals | Shapiro-Wilk (per group) | Use Kruskal-Wallis non-parametric alternative |
| Homogeneity of variance | Levene's test | Use Welch's ANOVA or report with caveat |
| Independence | Design-based (CRN pairs) | Paired analysis as sensitivity check |

---

## 5. Multiple Comparison Procedures

### 5.1 Tukey's Honest Significant Difference (HSD)

Used for **all pairwise** policy comparisons after a significant omnibus F-test.
Controls family-wise Type I error at α = 0.05 across all $\binom{k}{2}$ pairs.

$$\text{HSD} = q_{\alpha,k,N-k}\;\sqrt{\frac{MSE}{n}}$$

### 5.2 Bonferroni Correction

Applied when comparisons are pre-planned or when Tukey assumptions are questionable.
Adjusted significance level: $\alpha' = \alpha / m$ where $m$ is the number of
comparisons.

---

## 6. Confidence Interval Methodology

### 6.1 Standard CIs

For each policy–scenario combination:

$$\bar{X} \pm t_{\alpha/2,\,n-1}\;\frac{s}{\sqrt{n}}$$

with $n = 30$ replications.

### 6.2 CIs for Differences

For paired policy comparisons (leveraging CRN):

$$\bar{D} \pm t_{\alpha/2,\,n-1}\;\frac{s_D}{\sqrt{n}}$$

where $D_i = X_i^{A} - X_i^{B}$ is the paired difference for replication $i$.

### 6.3 Bootstrap CIs

If normality is rejected, we compute bias-corrected and accelerated (BCa) bootstrap
intervals with 10 000 resamples.

---

## 7. Effect Size Interpretation

### 7.1 Cohen's d (Pairwise)

$$d = \frac{\bar{X}_A - \bar{X}_B}{s_{\text{pooled}}}$$

| d | Interpretation |
|---|---------------|
| < 0.2 | Negligible |
| 0.2–0.5 | Small |
| 0.5–0.8 | Medium |
| > 0.8 | Large |

### 7.2 Eta-squared (η²) for ANOVA

$$\eta^2 = \frac{SS_{\text{effect}}}{SS_{\text{total}}}$$

| η² | Interpretation |
|----|---------------|
| < 0.01 | Negligible |
| 0.01–0.06 | Small |
| 0.06–0.14 | Medium |
| > 0.14 | Large |

---

## 8. Publication Standards

- All p-values reported to 3 decimal places; p < 0.001 where applicable.
- Effect sizes reported alongside p-values (APA 7th ed.).
- Figures at 300 DPI, vector-quality where feasible.
- Tables include 95% CIs in parentheses.
- Multiple-comparison adjustments stated explicitly.
- Statistical software: Python 3 with SciPy 1.x, statsmodels 0.14+.

---

## 9. References

- Banks, J. et al. (2010). *Discrete-Event System Simulation*, 5th ed.
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*.
- Law, A. M. (2015). *Simulation Modeling and Analysis*, 5th ed.
- Tukey, J. W. (1977). *Exploratory Data Analysis*.
