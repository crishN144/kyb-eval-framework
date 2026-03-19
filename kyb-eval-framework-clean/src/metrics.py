"""
Evaluation Metrics for KYB Compliance AI

Implements standard and domain-specific metrics for assessing
KYB verification system quality.
"""

from typing import List, Dict, Tuple


class KYBMetrics:
    """Compute evaluation metrics for KYB verification systems"""

    @staticmethod
    def confusion_matrix(predictions: List[str], ground_truth: List[str],
                         labels: List[str] = None) -> Dict[str, Dict[str, int]]:
        """
        Compute confusion matrix for multi-class classification

        Returns dict of dicts: matrix[true_label][predicted_label] = count
        """
        if labels is None:
            labels = sorted(set(ground_truth + predictions))

        matrix = {true_label: {pred_label: 0 for pred_label in labels}
                  for true_label in labels}

        for true, pred in zip(ground_truth, predictions):
            if true in labels and pred in labels:
                matrix[true][pred] += 1

        return matrix

    @staticmethod
    def precision_recall_f1(predictions: List[str], ground_truth: List[str],
                           positive_label: str = "fraudulent") -> Dict[str, float]:
        """
        Compute precision, recall, F1 for binary classification

        Args:
            predictions: List of predicted labels
            ground_truth: List of true labels
            positive_label: Which label to treat as "positive" class

        Returns:
            Dict with precision, recall, f1
        """
        # Convert to binary: positive_label vs. everything else
        pred_binary = [1 if p == positive_label else 0 for p in predictions]
        true_binary = [1 if t == positive_label else 0 for t in ground_truth]

        tp = sum(1 for p, t in zip(pred_binary, true_binary) if p == 1 and t == 1)
        fp = sum(1 for p, t in zip(pred_binary, true_binary) if p == 1 and t == 0)
        fn = sum(1 for p, t in zip(pred_binary, true_binary) if p == 0 and t == 1)
        tn = sum(1 for p, t in zip(pred_binary, true_binary) if p == 0 and t == 0)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn
        }

    @staticmethod
    def false_positive_rate(predictions: List[str], ground_truth: List[str],
                           positive_label: str = "fraudulent") -> float:
        """
        Compute false positive rate: FP / (FP + TN)

        Important metric for compliance: legitimate businesses wrongly rejected
        """
        pred_binary = [1 if p == positive_label else 0 for p in predictions]
        true_binary = [1 if t == positive_label else 0 for t in ground_truth]

        fp = sum(1 for p, t in zip(pred_binary, true_binary) if p == 1 and t == 0)
        tn = sum(1 for p, t in zip(pred_binary, true_binary) if p == 0 and t == 0)

        return fp / (fp + tn) if (fp + tn) > 0 else 0.0

    @staticmethod
    def false_negative_rate(predictions: List[str], ground_truth: List[str],
                           positive_label: str = "fraudulent") -> float:
        """
        Compute false negative rate: FN / (FN + TP)

        Important metric for compliance: fraudulent cases that slip through
        """
        pred_binary = [1 if p == positive_label else 0 for p in predictions]
        true_binary = [1 if t == positive_label else 0 for t in ground_truth]

        fn = sum(1 for p, t in zip(pred_binary, true_binary) if p == 0 and t == 1)
        tp = sum(1 for p, t in zip(pred_binary, true_binary) if p == 1 and t == 1)

        return fn / (fn + tp) if (fn + tp) > 0 else 0.0

    @staticmethod
    def adversarial_rejection_rate(predictions: List[str], ground_truth: List[str],
                                  adversarial_indices: List[int]) -> float:
        """
        Domain-specific metric: % of adversarial attacks correctly rejected

        Args:
            predictions: All predictions
            ground_truth: All ground truth labels
            adversarial_indices: Indices of adversarial test cases

        Returns:
            Percentage of adversarial cases correctly identified
        """
        if not adversarial_indices:
            return 0.0

        adversarial_correct = 0
        for idx in adversarial_indices:
            # Adversarial cases should be rejected (predicted as fraudulent)
            if predictions[idx] in ["reject", "fraudulent"]:
                adversarial_correct += 1

        return adversarial_correct / len(adversarial_indices)

    @staticmethod
    def legitimate_approval_rate(predictions: List[str], ground_truth: List[str],
                                legitimate_indices: List[int]) -> float:
        """
        Domain-specific metric: % of legitimate businesses correctly approved

        Args:
            predictions: All predictions
            ground_truth: All ground truth labels
            legitimate_indices: Indices of legitimate test cases

        Returns:
            Percentage of legitimate cases correctly approved
        """
        if not legitimate_indices:
            return 0.0

        legitimate_correct = 0
        for idx in legitimate_indices:
            # Legitimate cases should be approved
            if predictions[idx] in ["approve", "legitimate"]:
                legitimate_correct += 1

        return legitimate_correct / len(legitimate_indices)

    @staticmethod
    def edge_case_escalation_rate(predictions: List[str], ground_truth: List[str],
                                 edge_case_indices: List[int]) -> float:
        """
        Domain-specific metric: % of edge cases correctly escalated for manual review

        Args:
            predictions: All predictions
            ground_truth: All ground truth labels
            edge_case_indices: Indices of edge case test cases

        Returns:
            Percentage of edge cases correctly escalated
        """
        if not edge_case_indices:
            return 0.0

        edge_correct = 0
        for idx in edge_case_indices:
            # Edge cases should be escalated (predicted as ambiguous)
            if predictions[idx] in ["escalate", "ambiguous"]:
                edge_correct += 1

        return edge_correct / len(edge_case_indices)

    @staticmethod
    def overall_accuracy(predictions: List[str], ground_truth: List[str]) -> float:
        """Compute overall accuracy"""
        correct = sum(1 for p, t in zip(predictions, ground_truth) if p == t)
        return correct / len(predictions) if predictions else 0.0

    @staticmethod
    def compute_all_metrics(predictions: List[str], ground_truth: List[str],
                          test_cases: List[Dict]) -> Dict:
        """
        Compute comprehensive metric suite

        Args:
            predictions: Predicted labels for each test case
            ground_truth: True labels for each test case
            test_cases: Original test case objects (to extract categories)

        Returns:
            Dict containing all metrics
        """
        # Extract indices by category
        legitimate_indices = [i for i, tc in enumerate(test_cases)
                             if tc.get('category') == 'legitimate']
        adversarial_indices = [i for i, tc in enumerate(test_cases)
                              if tc.get('category') == 'adversarial']
        edge_case_indices = [i for i, tc in enumerate(test_cases)
                            if tc.get('category') == 'edge_case']

        # Standard metrics
        # TODO: add per-class precision/recall for three-way classification (legitimate/fraudulent/ambiguous)
        prf = KYBMetrics.precision_recall_f1(predictions, ground_truth, positive_label="fraudulent")

        # Domain-specific metrics
        results = {
            "standard_metrics": {
                "precision": prf["precision"],
                "recall": prf["recall"],
                "f1_score": prf["f1"],
                "overall_accuracy": KYBMetrics.overall_accuracy(predictions, ground_truth),
                "true_positives": prf["true_positives"],
                "false_positives": prf["false_positives"],
                "false_negatives": prf["false_negatives"],
                "true_negatives": prf["true_negatives"]
            },
            "domain_specific_metrics": {
                "adversarial_rejection_rate": KYBMetrics.adversarial_rejection_rate(
                    predictions, ground_truth, adversarial_indices
                ),
                "legitimate_approval_rate": KYBMetrics.legitimate_approval_rate(
                    predictions, ground_truth, legitimate_indices
                ),
                "edge_case_escalation_rate": KYBMetrics.edge_case_escalation_rate(
                    predictions, ground_truth, edge_case_indices
                ),
                "false_positive_rate": KYBMetrics.false_positive_rate(
                    predictions, ground_truth, positive_label="fraudulent"
                ),
                "false_negative_rate": KYBMetrics.false_negative_rate(
                    predictions, ground_truth, positive_label="fraudulent"
                )
            },
            "confusion_matrix": KYBMetrics.confusion_matrix(predictions, ground_truth),
            "test_case_counts": {
                "total": len(test_cases),
                "legitimate": len(legitimate_indices),
                "adversarial": len(adversarial_indices),
                "edge_cases": len(edge_case_indices)
            }
        }

        return results


def format_metrics_report(metrics: Dict) -> str:
    """Format metrics as readable markdown report"""
    report = []

    report.append("# KYB Verification System Evaluation Report\n")
    report.append(f"**Test Cases:** {metrics['test_case_counts']['total']} total ")
    report.append(f"({metrics['test_case_counts']['legitimate']} legitimate, ")
    report.append(f"{metrics['test_case_counts']['adversarial']} adversarial, ")
    report.append(f"{metrics['test_case_counts']['edge_cases']} edge cases)\n")

    report.append("\n## Standard Metrics\n")
    std = metrics['standard_metrics']
    report.append(f"- **Precision:** {std['precision']:.1%}")
    report.append(f"- **Recall:** {std['recall']:.1%}")
    report.append(f"- **F1 Score:** {std['f1_score']:.1%}")
    report.append(f"- **Overall Accuracy:** {std['overall_accuracy']:.1%}")

    report.append("\n\n## Domain-Specific Metrics\n")
    dom = metrics['domain_specific_metrics']
    report.append(f"- **Adversarial Rejection Rate:** {dom['adversarial_rejection_rate']:.1%} ")
    report.append(f"({int(dom['adversarial_rejection_rate'] * metrics['test_case_counts']['adversarial'])}/")
    report.append(f"{metrics['test_case_counts']['adversarial']} attacks correctly blocked)")

    report.append(f"\n- **Legitimate Approval Rate:** {dom['legitimate_approval_rate']:.1%} ")
    report.append(f"({int(dom['legitimate_approval_rate'] * metrics['test_case_counts']['legitimate'])}/")
    report.append(f"{metrics['test_case_counts']['legitimate']} legitimate businesses approved)")

    report.append(f"\n- **Edge Case Escalation Rate:** {dom['edge_case_escalation_rate']:.1%} ")
    report.append(f"({int(dom['edge_case_escalation_rate'] * metrics['test_case_counts']['edge_cases'])}/")
    report.append(f"{metrics['test_case_counts']['edge_cases']} ambiguous cases escalated)")

    report.append(f"\n- **False Positive Rate:** {dom['false_positive_rate']:.1%}")
    report.append(f"\n- **False Negative Rate:** {dom['false_negative_rate']:.1%}")

    report.append("\n\n## Confusion Matrix\n")
    report.append("```")
    cm = metrics['confusion_matrix']
    labels = sorted(cm.keys())

    # Header
    header = "True \\ Pred".ljust(15) + "".join([l.ljust(15) for l in labels])
    report.append(header)
    report.append("-" * len(header))

    # Rows
    for true_label in labels:
        row = true_label.ljust(15) + "".join([str(cm[true_label].get(pred_label, 0)).ljust(15)
                                              for pred_label in labels])
        report.append(row)
    report.append("```")

    return "\n".join(report)
