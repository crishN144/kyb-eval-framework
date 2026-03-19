# KYB Verifier Comparison Report
Comparing Rule-Based vs Scoring-Based verification approaches

---

## Standard Metrics Comparison

| Metric | Rule-Based | Scoring-Based | Difference |
|--------|-----------|--------------|------------|
| Overall Accuracy | 0.0% | 0.0% | 0.0% |
| Precision | 0.0% | 0.0% | 0.0% |
| Recall | 0.0% | 0.0% | 0.0% |
| F1 Score | 0.0% | 0.0% | 0.0% |

## Domain-Specific Metrics Comparison

| Metric | Rule-Based | Scoring-Based | Difference |
|--------|-----------|--------------|------------|
| Adversarial Rejection Rate | 70.0% | 55.0% | -15.0% |
| Legitimate Approval Rate | 95.0% | 95.0% | 0.0% |
| Edge Case Escalation Rate | 30.0% | 30.0% | 0.0% |
| False Positive Rate | 3.3% | 3.3% | 0.0% |
| False Negative Rate | 30.0% | 45.0% | +15.0% |

## Analysis

**Tie** (Both achieve F1: 0.0%)

**Key Trade-offs:**

- Rule-based has lower false negative rate (30.0% vs 45.0%)

**Recommendation:**
The scoring-based approach allows threshold tuning for precision/recall trade-offs. Production systems should use scoring with dynamic thresholds adjusted based on fraud rates.
