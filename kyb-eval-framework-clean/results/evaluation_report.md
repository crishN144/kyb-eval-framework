# KYB Verification System Evaluation Report

**Test Cases:** 50 total 
(20 legitimate, 
20 adversarial, 
10 edge cases)


## Standard Metrics

- **Precision:** 93.3%
- **Recall:** 70.0%
- **F1 Score:** 80.0%
- **Overall Accuracy:** 72.0%


## Domain-Specific Metrics

- **Adversarial Rejection Rate:** 70.0% 
(14/
20 attacks correctly blocked)

- **Legitimate Approval Rate:** 95.0% 
(19/
20 legitimate businesses approved)

- **Edge Case Escalation Rate:** 30.0% 
(3/
10 ambiguous cases escalated)

- **False Positive Rate:** 3.3%

- **False Negative Rate:** 30.0%


## Confusion Matrix

```
True \ Pred    ambiguous      fraudulent     legitimate     
------------------------------------------------------------
ambiguous      3              1              6              
fraudulent     1              14             5              
legitimate     1              0              19             
```

## Failure Analysis

**Total Failures:** 14

### Failure Breakdown by Type:

- **Edge Case Wrongly Approved:** 6 cases
  - Examples: EDGE-009, EDGE-006, EDGE-004 (and 3 more)
- **False Negative Name Variation:** 2 cases
  - Examples: ADV-016, ADV-015
- **False Negative Stale Document:** 2 cases
  - Examples: ADV-014, ADV-013
- **Edge Case Wrongly Rejected:** 1 cases
  - Examples: EDGE-002
- **False Negative Dormant Company:** 1 cases
  - Examples: ADV-019
- **False Negative Recent Website:** 1 cases
  - Examples: ADV-020
- **Other Failure:** 1 cases
  - Examples: LEG-009

## Recommendations
1. **Reduce false positives**: Newly incorporated companies (e.g., LEG-009) trigger escalation even when legitimate. Consider risk-based thresholds instead of blanket date cutoffs
2. **Refine edge case handling**: Implement confidence scoring to better identify ambiguous cases for escalation
3. **Enhance adversarial robustness**: Current adversarial detection rate (70.0%) is below target (80%+)