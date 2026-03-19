"""
KYB Verification System Evaluator

Core evaluation framework for assessing KYB/AML compliance AI decision quality.
Based on systematic evaluation methodology from arXiv:2601.14479.
"""

import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import random

from metrics import KYBMetrics, format_metrics_report


@dataclass
class EvaluationResult:
    """Single test case evaluation result"""
    case_id: str
    category: str
    predicted: str
    ground_truth: str
    correct: bool
    failure_type: Optional[str]  # Type of failure if incorrect


class ScoringKYBVerifier:
    """
    Risk-scoring based verifier using weighted signals

    Assigns risk score (0-100) and uses configurable thresholds for decisions.
    More flexible than pure rules - allows threshold tuning for precision/recall trade-offs.

    Scoring approach catches edge cases better than rules because ambiguous signals
    (recent incorporation + virtual office = 20 points) naturally land in the
    escalation zone rather than defaulting to approve.
    """

    def __init__(self, reject_threshold: int = 40, escalate_threshold: int = 8):
        """
        Args:
            reject_threshold: Risk score above which to reject (default 40)
            escalate_threshold: Risk score above which to escalate (default 8)

        Thresholds calibrated so single strong signal (address mismatch = 50) triggers
        rejection on its own. Escalation at 8 catches edge cases like virtual offices (10),
        recent incorporations (10), and previous names (8).
        """
        self.reject_threshold = reject_threshold
        self.escalate_threshold = escalate_threshold

    def _normalize_company_name(self, name: str) -> str:
        """Normalize common UK company name variations"""
        n = name.upper().strip()
        # Standard Companies House equivalences
        n = n.replace('LIMITED', 'LTD')
        n = n.replace('PUBLIC LIMITED COMPANY', 'PLC')
        n = n.replace('&', 'AND')
        # Remove extra whitespace
        n = ' '.join(n.split())
        return n

    def _name_consistency_score(self, company_name: str, doc_name: str) -> int:
        """Check name consistency with normalization for common variations"""
        norm_company = self._normalize_company_name(company_name)
        norm_doc = self._normalize_company_name(doc_name)

        if norm_company == norm_doc:
            return 0  # Names match after normalization

        # Check if one is substring of other (partial match)
        if norm_company in norm_doc or norm_doc in norm_company:
            return 15  # Partial match - suspicious but not definitive

        return 35  # Completely different names - strong fraud signal

    def _document_freshness_score(self, doc_date_str: str) -> int:
        """Check if documents are within acceptable verification window"""
        if not doc_date_str:
            return 20  # No date at all is suspicious

        try:
            from datetime import datetime
            doc_date = datetime.strptime(doc_date_str, '%Y-%m-%d')
            days_old = (datetime.now() - doc_date).days

            if days_old > 365:
                return 30  # Over 12 months - outside standard verification window
            elif days_old > 180:
                return 15  # 6-12 months - getting stale
            elif days_old < 0:
                return 25  # Future date - likely fabricated
            return 0
        except (ValueError, TypeError):
            return 10  # Unparseable date is mildly suspicious

    def _website_credibility_score(self, document_data: Dict) -> int:
        """Evaluate website credibility based on URL patterns and domain age"""
        website = document_data.get('website', '')
        if isinstance(website, dict):
            url = website.get('url', '').lower()
            domain_date = website.get('domain_registration_date', '')
        elif isinstance(website, str):
            url = website.lower()
            domain_date = ''
        else:
            return 0

        score = 0

        # Known suspicious patterns
        suspicious = ['pastebin', 'github.io', 'expired-domain']
        if any(s in url for s in suspicious):
            score += 40

        # Domain registered very recently for established company
        if domain_date:
            try:
                from datetime import datetime
                reg_date = datetime.strptime(domain_date, '%Y-%m-%d')
                days_since = (datetime.now() - reg_date).days
                if days_since < 30:
                    score += 25  # Brand new domain for existing company
            except (ValueError, TypeError):
                pass

        return score

    def verify_case(self, test_case: Dict) -> str:
        """Calculate risk score and make decision based on thresholds"""
        company = test_case.get('company_data', {})
        docs = test_case.get('document_data', {})

        risk_score = 0

        # Signal 1: Document completeness (0-25 points)
        bill = docs.get('utility_bill', {})
        completeness = bill.get('completeness', 1.0)
        if completeness < 0.3:
            risk_score += 25
        elif completeness < 0.7:
            risk_score += 15

        # Signal 2: Address consistency (0-50 points)
        company_addr = company.get('registered_address', '')
        bill_addr = bill.get('address', '')
        if company_addr and bill_addr:
            company_pc = company_addr.split(',')[-1].strip()
            bill_pc = bill_addr.split(',')[-1].strip()
            if company_pc != bill_pc:
                risk_score += 50

        # Signal 3: Website credibility (0-40 points)
        risk_score += self._website_credibility_score(docs)

        # Signal 4: Name consistency with normalization (0-35 points)
        company_name = company.get('company_name', '')
        doc_name = bill.get('account_holder', '')
        if company_name and doc_name:
            risk_score += self._name_consistency_score(company_name, doc_name)

        # Signal 5: Document freshness (0-30 points)
        doc_date = bill.get('date', '')
        risk_score += self._document_freshness_score(doc_date)

        # Signal 6: Company status signals (0-20 points)
        inc_date = company.get('date_of_incorporation',
                               company.get('incorporation_date', ''))
        if inc_date and ('2026' in inc_date or '2025' in inc_date):
            risk_score += 10

        status = company.get('status', '').lower()
        if 'dormant' in status or 'strike-off' in status:
            risk_score += 15

        if company.get('office_type') == 'virtual':
            risk_score += 10

        if 'previous_names' in company:
            risk_score += 8

        # Decision based on aggregate score
        if risk_score >= self.reject_threshold:
            return "reject"
        elif risk_score >= self.escalate_threshold:
            return "escalate"
        return "approve"


class SimpleKYBVerifier:
    """
    Simple rule-based KYB verifier for demonstration purposes

    In production, this would be replaced by an actual ML model or LLM-based system.
    This baseline implementation uses heuristic rules to make decisions.
    """

    def verify_case(self, test_case: Dict) -> str:
        """
        Make verification decision for a test case

        Returns: "approve", "reject", or "escalate"
        """
        company_data = test_case.get('company_data', {})
        document_data = test_case.get('document_data', {})

        # Rule 1: Check document completeness
        # TODO: add document date freshness check - stale docs (14+ months) are slipping through
        if 'utility_bill' in document_data:
            bill = document_data['utility_bill']
            completeness = bill.get('completeness', 1.0)

            # Reject if blank or very incomplete
            if completeness < 0.3:
                return "reject"

        # Rule 2: Cross-check registered address with utility bill
        # Exact postcode match only - fuzzy matching would catch manipulation attacks
        # but risks false positives on legitimate address variations (typos, formatting)
        comp_addr = company_data.get('registered_address', '')
        if 'utility_bill' in document_data:
            bill = document_data['utility_bill']
            bill_addr = bill.get('address', '')

            if comp_addr and bill_addr:
                # Extract postcodes for comparison
                comp_postcode = comp_addr.split(',')[-1].strip()
                bill_postcode = bill_addr.split(',')[-1].strip()

                if comp_postcode != bill_postcode:
                    return "reject"

        # Rule 3: Check for suspicious website signals
        # TODO: add domain age check via WHOIS - recent registrations are slipping through
        if 'website' in document_data:
            website = document_data['website']
            # Handle both string and dict formats
            if isinstance(website, str):
                url = website.lower()
            else:
                url = website.get('url', '').lower()

            suspicious_domains = ['pastebin', 'github.io', 'expired-domain']
            if any(domain in url for domain in suspicious_domains):
                return "reject"

        # Rule 4: Handle edge cases - newly registered companies
        # Check both field names for compatibility
        inc_date = company_data.get('date_of_incorporation', company_data.get('incorporation_date', ''))
        if inc_date:
            # Recent incorporation = higher risk, should escalate for review
            if '2026' in inc_date or '2025' in inc_date:
                return "escalate"

        # Rule 5: Handle virtual offices
        if company_data.get('office_type') == 'virtual':
            return "escalate"

        # Rule 6: Check for dormant or strike-off status
        status = company_data.get('status', '').lower()
        if 'dormant' in status or 'strike-off' in status:
            return "escalate"

        # Rule 7: Recent name changes indicate potential instability
        if 'previous_names' in company_data:
            return "escalate"

        # Rule 6: Handle recent address changes
        if 'note' in document_data and 'address change' in document_data['note'].lower():
            return "escalate"

        # Default: approve if no red flags
        return "approve"


class KYBEvaluationFramework:
    """
    Systematic evaluation framework for KYB verification systems

    Based on evaluation methodology from arXiv:2601.14479:
    - Systematic test case design
    - Failure mode categorization
    - Multiple evaluation metrics
    - Actionable recommendations
    """

    def __init__(self, test_cases: List[Dict]):
        self.test_cases = test_cases
        self.results: List[EvaluationResult] = []

    def run_evaluation(self, verifier: Optional[SimpleKYBVerifier] = None) -> Dict:
        """
        Run evaluation on all test cases

        Args:
            verifier: KYB verification system to evaluate.
                     If None, uses default SimpleKYBVerifier

        Returns:
            Comprehensive evaluation results
        """
        if verifier is None:
            verifier = SimpleKYBVerifier()

        print("=" * 80)
        print("Running KYB Verification System Evaluation")
        print("=" * 80)
        print(f"Total test cases: {len(self.test_cases)}\n")

        # Run verification on each test case
        predictions = []
        ground_truth = []

        for i, test_case in enumerate(self.test_cases, 1):
            # Get prediction from verifier
            prediction = verifier.verify_case(test_case)

            # Get ground truth
            expected = test_case.get('expected_outcome')

            # Normalize labels for comparison
            pred_label = self._normalize_label(prediction)
            true_label = self._normalize_label(expected)

            predictions.append(pred_label)
            ground_truth.append(true_label)

            # Determine correctness
            correct = (pred_label == true_label)

            # Categorize failure if incorrect
            failure_type = None
            if not correct:
                failure_type = self._categorize_failure(test_case, pred_label, true_label)

            result = EvaluationResult(
                case_id=test_case.get('case_id'),
                category=test_case.get('category'),
                predicted=pred_label,
                ground_truth=true_label,
                correct=correct,
                failure_type=failure_type
            )

            self.results.append(result)

            # Print progress
            status = "✓" if correct else "✗"
            print(f"  [{i:3d}/{len(self.test_cases)}] {status} {test_case.get('case_id')} "
                  f"({test_case.get('category')})")

        print("\n" + "=" * 80)
        print("Evaluation Complete")
        print("=" * 80)

        # Compute metrics
        metrics = KYBMetrics.compute_all_metrics(predictions, ground_truth, self.test_cases)

        # Add failure analysis
        metrics['failure_analysis'] = self._analyze_failures()

        return metrics

    def _normalize_label(self, label: str) -> str:
        """
        Normalize labels to consistent format

        Maps various label formats to: "legitimate", "fraudulent", "ambiguous"
        """
        if not label:
            return "unknown"

        label = label.lower()

        if label in ["approve", "legitimate"]:
            return "legitimate"
        elif label in ["reject", "fraudulent"]:
            return "fraudulent"
        elif label in ["escalate", "ambiguous"]:
            return "ambiguous"
        else:
            return label

    def _categorize_failure(self, test_case: Dict, predicted: str, ground_truth: str) -> str:
        """
        Categorize type of failure for systematic analysis

        Returns specific failure category for root cause analysis
        """
        category = test_case.get('category')
        attack_type = test_case.get('attack_type')

        # False Negative: Fraudulent case approved/escalated
        if ground_truth == "fraudulent" and predicted != "fraudulent":
            if attack_type:
                return f"false_negative_{attack_type}"
            return "false_negative_adversarial"

        # False Positive: Legitimate case rejected
        if ground_truth == "legitimate" and predicted == "fraudulent":
            return "false_positive_legitimate_rejected"

        # Edge case mishandling: Should escalate but didn't
        if ground_truth == "ambiguous" and predicted != "ambiguous":
            if predicted == "fraudulent":
                return "edge_case_wrongly_rejected"
            else:
                return "edge_case_wrongly_approved"

        return "other_failure"

    def _analyze_failures(self) -> Dict:
        """
        Systematic failure mode analysis

        Categorizes and counts failures by type for actionable insights
        """
        failure_counts = {}
        failure_examples = {}

        for result in self.results:
            if not result.correct and result.failure_type:
                # Count failures by type
                failure_counts[result.failure_type] = failure_counts.get(result.failure_type, 0) + 1

                # Store example case IDs
                if result.failure_type not in failure_examples:
                    failure_examples[result.failure_type] = []
                failure_examples[result.failure_type].append(result.case_id)

        # Sort by count
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "failure_counts": dict(sorted_failures),
            "failure_examples": failure_examples,
            "total_failures": sum(failure_counts.values())
        }

    def generate_report(self, metrics: Dict, output_path: Optional[str] = None) -> str:
        """
        Generate comprehensive evaluation report

        Args:
            metrics: Evaluation metrics from run_evaluation()
            output_path: Optional file path to save report

        Returns:
            Formatted report string
        """
        # Use metrics formatting
        report = format_metrics_report(metrics)

        # Add failure analysis
        report += "\n\n## Failure Analysis\n"
        failure_analysis = metrics.get('failure_analysis', {})

        if failure_analysis.get('total_failures', 0) > 0:
            report += f"\n**Total Failures:** {failure_analysis['total_failures']}\n"

            report += "\n### Failure Breakdown by Type:\n"
            for failure_type, count in failure_analysis.get('failure_counts', {}).items():
                examples = failure_analysis.get('failure_examples', {}).get(failure_type, [])
                example_str = ", ".join(examples[:3])  # Show first 3 examples
                if len(examples) > 3:
                    example_str += f" (and {len(examples) - 3} more)"

                # Format failure type as readable text
                readable_type = failure_type.replace('_', ' ').title()
                report += f"\n- **{readable_type}:** {count} cases"
                report += f"\n  - Examples: {example_str}"
        else:
            report += "\nNo failures detected. All test cases passed.\n"

        # Add recommendations
        report += "\n\n## Recommendations\n"
        report += self._generate_recommendations(metrics)

        # Save to file if specified
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {output_path}")

        return report

    def _generate_recommendations(self, metrics: Dict) -> str:
        """Generate actionable recommendations based on failure patterns"""
        recommendations = []
        rec_num = 1

        failure_analysis = metrics.get('failure_analysis', {})
        failure_counts = failure_analysis.get('failure_counts', {})

        # Check for specific failure patterns
        if any('blank_document' in f for f in failure_counts.keys()):
            recommendations.append(
                f"{rec_num}. **Strengthen document completeness validation**: "
                "Implement stricter checks for blank or incomplete documents"
            )
            rec_num += 1

        if any('address_mismatch' in f for f in failure_counts.keys()):
            recommendations.append(
                f"{rec_num}. **Improve address consistency checks**: "
                "Add cross-field validation between company registration and proof of address"
            )
            rec_num += 1

        if any('false_positive' in f or 'other_failure' in f for f in failure_counts.keys()):
            recommendations.append(
                f"{rec_num}. **Reduce false positives**: "
                "Newly incorporated companies (e.g., LEG-009) trigger escalation even when legitimate. "
                "Consider risk-based thresholds instead of blanket date cutoffs"
            )
            rec_num += 1

        if any('edge_case' in f for f in failure_counts.keys()):
            recommendations.append(
                f"{rec_num}. **Refine edge case handling**: "
                "Implement confidence scoring to better identify ambiguous cases for escalation"
            )
            rec_num += 1

        dom = metrics.get('domain_specific_metrics', {})
        if dom.get('adversarial_rejection_rate', 0) < 0.8:
            recommendations.append(
                f"{rec_num}. **Enhance adversarial robustness**: "
                f"Current adversarial detection rate ({dom['adversarial_rejection_rate']:.1%}) "
                "is below target (80%+)"
            )
            rec_num += 1

        if not recommendations:
            recommendations.append("System performing well across all test categories")

        return "\n".join(recommendations)


def generate_comparison_report(rule_metrics: Dict, score_metrics: Dict) -> str:
    """Generate side-by-side comparison of two verifiers"""
    report = ["# KYB Verifier Comparison Report\n"]
    report.append("Comparing Rule-Based vs Scoring-Based verification approaches\n\n")
    report.append("---\n\n")

    # Standard metrics comparison
    report.append("## Standard Metrics Comparison\n\n")
    report.append("| Metric | Rule-Based | Scoring-Based | Difference |\n")
    report.append("|--------|-----------|--------------|------------|\n")

    rule_std = rule_metrics
    score_std = score_metrics

    metrics_to_compare = [
        ("Overall Accuracy", "accuracy"),
        ("Precision", "precision"),
        ("Recall", "recall"),
        ("F1 Score", "f1_score"),
    ]

    for display_name, key in metrics_to_compare:
        rule_val = rule_std.get(key, 0)
        score_val = score_std.get(key, 0)
        diff = score_val - rule_val
        diff_str = f"+{diff:.1%}" if diff > 0 else f"{diff:.1%}"

        report.append(f"| {display_name} | {rule_val:.1%} | {score_val:.1%} | {diff_str} |\n")

    # Domain metrics comparison
    report.append("\n## Domain-Specific Metrics Comparison\n\n")
    report.append("| Metric | Rule-Based | Scoring-Based | Difference |\n")
    report.append("|--------|-----------|--------------|------------|\n")

    domain_metrics = [
        ("Adversarial Rejection Rate", "adversarial_rejection_rate"),
        ("Legitimate Approval Rate", "legitimate_approval_rate"),
        ("Edge Case Escalation Rate", "edge_case_escalation_rate"),
        ("False Positive Rate", "false_positive_rate"),
        ("False Negative Rate", "false_negative_rate"),
    ]

    rule_dom = rule_metrics.get('domain_specific_metrics', {})
    score_dom = score_metrics.get('domain_specific_metrics', {})

    for display_name, key in domain_metrics:
        rule_val = rule_dom.get(key, 0)
        score_val = score_dom.get(key, 0)
        diff = score_val - rule_val
        diff_str = f"+{diff:.1%}" if diff > 0 else f"{diff:.1%}"

        report.append(f"| {display_name} | {rule_val:.1%} | {score_val:.1%} | {diff_str} |\n")

    # Analysis
    report.append("\n## Analysis\n\n")

    # Determine winner
    rule_f1 = rule_std.get('f1_score', 0)
    score_f1 = score_std.get('f1_score', 0)

    if score_f1 > rule_f1:
        report.append(f"**Winner: Scoring-Based** (F1: {score_f1:.1%} vs {rule_f1:.1%})\n\n")
    elif rule_f1 > score_f1:
        report.append(f"**Winner: Rule-Based** (F1: {rule_f1:.1%} vs {score_f1:.1%})\n\n")
    else:
        report.append(f"**Tie** (Both achieve F1: {rule_f1:.1%})\n\n")

    # Key differences
    report.append("**Key Trade-offs:**\n\n")

    # Compare FPR
    rule_fpr = rule_dom.get('false_positive_rate', 0)
    score_fpr = score_dom.get('false_positive_rate', 0)
    if abs(score_fpr - rule_fpr) > 0.01:
        better = "Scoring-based" if score_fpr < rule_fpr else "Rule-based"
        report.append(f"- {better} has lower false positive rate ({min(rule_fpr, score_fpr):.1%} vs {max(rule_fpr, score_fpr):.1%})\n")

    # Compare FNR
    rule_fnr = rule_dom.get('false_negative_rate', 0)
    score_fnr = score_dom.get('false_negative_rate', 0)
    if abs(score_fnr - rule_fnr) > 0.01:
        better = "Scoring-based" if score_fnr < rule_fnr else "Rule-based"
        report.append(f"- {better} has lower false negative rate ({min(rule_fnr, score_fnr):.1%} vs {max(rule_fnr, score_fnr):.1%})\n")

    # Edge case handling
    rule_esc = rule_dom.get('edge_case_escalation_rate', 0)
    score_esc = score_dom.get('edge_case_escalation_rate', 0)
    if abs(score_esc - rule_esc) > 0.05:
        better = "Scoring-based" if score_esc > rule_esc else "Rule-based"
        report.append(f"- {better} escalates more edge cases ({max(rule_esc, score_esc):.1%} vs {min(rule_esc, score_esc):.1%})\n")

    report.append("\n**Recommendation:**\n")
    report.append("The scoring-based approach allows threshold tuning for precision/recall trade-offs. ")
    report.append("Production systems should use scoring with dynamic thresholds adjusted based on fraud rates.\n")

    return "".join(report)


def main():
    """Run evaluation on test cases"""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate KYB verification system")
    parser.add_argument("--test-cases", default="data/test_cases.json",
                       help="Path to test cases JSON file")
    parser.add_argument("--output", default="results/evaluation_report.md",
                       help="Output report path")
    parser.add_argument("--compare", action="store_true",
                       help="Compare rule-based vs scoring-based verifiers")

    args = parser.parse_args()

    # Load test cases
    print(f"Loading test cases from: {args.test_cases}")
    with open(args.test_cases, 'r') as f:
        test_cases = json.load(f)

    print(f"Loaded {len(test_cases)} test cases\n")

    if args.compare:
        # Comparative evaluation mode
        print("=" * 80)
        print("COMPARATIVE EVALUATION: Rule-Based vs Scoring-Based Verifiers")
        print("=" * 80 + "\n")

        # Run rule-based verifier
        print("[1/2] Evaluating Rule-Based Verifier...")
        framework1 = KYBEvaluationFramework(test_cases)
        rule_metrics = framework1.run_evaluation(SimpleKYBVerifier())

        print("\n[2/2] Evaluating Scoring-Based Verifier...")
        framework2 = KYBEvaluationFramework(test_cases)
        score_metrics = framework2.run_evaluation(ScoringKYBVerifier())

        # Generate comparison report
        comparison_report = generate_comparison_report(rule_metrics, score_metrics)

        # Save comparison
        comparison_path = args.output.replace('.md', '_comparison.md')
        with open(comparison_path, 'w') as f:
            f.write(comparison_report)

        print(f"\nComparison report saved to: {comparison_path}")
        print("\n" + "=" * 80)
        print(comparison_report)
        print("=" * 80)

    else:
        # Single verifier evaluation (default: rule-based)
        framework = KYBEvaluationFramework(test_cases)
        metrics = framework.run_evaluation()
        report = framework.generate_report(metrics, args.output)

        print("\n" + "=" * 80)
        print(report)
        print("=" * 80)


if __name__ == "__main__":
    main()
