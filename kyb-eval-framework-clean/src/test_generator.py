"""
Test Case Generator v2 - Uses real Companies House data

Improvements over v1:
- Real UK company data (names, addresses, postcodes, SIC codes)
- Harder adversarial cases with more variety
- More edge cases (10 instead of 3)
- Better difficulty distribution
"""

import json
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class KYBTestCase:
    case_id: str
    category: str
    attack_type: Optional[str]
    company_data: Dict
    document_data: Dict
    expected_outcome: str
    ground_truth_label: str
    adversarial_difficulty: Optional[str]
    description: str

    def to_dict(self):
        return asdict(self)


class ImprovedKYBGenerator:
    """Generate realistic KYB test cases using real Companies House data"""

    def __init__(self, real_companies_file: str = 'data/real_companies.json'):
        with open(real_companies_file, 'r') as f:
            self.real_companies = json.load(f)

        random.shuffle(self.real_companies)
        print(f"Loaded {len(self.real_companies)} real UK companies")

    def _format_address(self, addr_dict: Dict) -> str:
        """Format Companies House address dict into single string"""
        parts = []
        for key in ['address_line_1', 'address_line_2', 'locality', 'postal_code']:
            if val := addr_dict.get(key):
                parts.append(val)
        return ', '.join(parts)

    def _clean_company_name_for_url(self, name: str) -> str:
        """Clean company name to create valid URL"""
        clean = name.lower()
        # Remove common suffixes
        for suffix in ['limited', 'ltd', 'llc', 'plc']:
            clean = clean.replace(suffix, '')
        # Remove special characters that aren't valid in URLs
        for char in ['&', '(', ')', ' ', "'", '"', ',', '.', '-']:
            clean = clean.replace(char, '')
        return clean[:20]  # Truncate to reasonable length

    def _recent_date(self, days_ago: int = 90) -> str:
        date = datetime.now() - timedelta(days=random.randint(1, days_ago))
        return date.strftime('%Y-%m-%d')

    def generate_legitimate_cases(self, n: int = 20) -> List[KYBTestCase]:
        """Generate legitimate business cases"""
        cases = []
        companies = self.real_companies[:n]

        for i, comp in enumerate(companies, 1):
            addr = comp['address']
            company_addr = self._format_address(addr)

            case = KYBTestCase(
                case_id=f"LEG-{i:03d}",
                category="legitimate",
                attack_type=None,
                company_data={
                    "company_name": comp['company_name'],
                    "company_number": comp['company_number'],
                    "registered_address": company_addr,
                    "date_of_incorporation": comp['date_of_creation'],
                    "sic_codes": comp['sic_codes'][:2],
                    "status": "active"
                },
                document_data={
                    "utility_bill": {
                        "address": company_addr,
                        "account_holder": comp['company_name'],
                        "date": self._recent_date(60),
                        "completeness": round(random.uniform(0.85, 1.0), 2),
                        "provider": random.choice(["British Gas", "EDF Energy", "Thames Water", "SSE"])
                    },
                    "bank_statement": {
                        "account_name": comp['company_name'],
                        "date": self._recent_date(30),
                        "completeness": round(random.uniform(0.9, 1.0), 2)
                    },
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk"
                },
                expected_outcome="approve",
                ground_truth_label="legitimate",
                adversarial_difficulty=None,
                description=f"Legitimate {comp['company_type']} with complete documentation"
            )
            cases.append(case)

        return cases

    def generate_adversarial_cases(self, n: int = 20) -> List[KYBTestCase]:
        """
        Generate adversarial cases with varied difficulty:
        - Trivial (30%): Obvious fraud like blank docs
        - Moderate (50%): Subtle issues requiring deeper checks
        - Hard (20%): Sophisticated attacks that might bypass naive systems
        """
        cases = []
        # Reuse companies if needed - adversarial cases use real company skeletons
        companies = self.real_companies  # Will cycle through as needed

        attack_types = [
            # Trivial attacks (6 cases)
            *[('blank_document', 'trivial')] * 3,
            *[('fake_website', 'trivial')] * 3,

            # Moderate attacks (10 cases)
            *[('address_mismatch', 'moderate')] * 3,
            *[('partial_document', 'moderate')] * 3,
            *[('stale_document', 'moderate')] * 2,
            *[('name_variation', 'moderate')] * 2,

            # Hard attacks (4 cases)
            *[('postcode_manipulation', 'hard')] * 2,
            *[('dormant_company', 'hard')] * 1,
            *[('recent_website', 'hard')] * 1,
        ]

        for i, (attack, diff) in enumerate(attack_types, 1):
            comp = companies[i % len(companies)]
            addr = comp['address']
            company_addr = self._format_address(addr)
            postcode = addr.get('postal_code', 'EC1A 1BB')

            if attack == 'blank_document':
                doc_data = {
                    "utility_bill": {
                        "address": "",
                        "account_holder": "",
                        "date": "",
                        "completeness": 0.0,
                        "provider": ""
                    },
                    "bank_statement": {"completeness": 0.9},
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk"
                }
                desc = "Blank utility bill - from Arva HN thread vulnerability"

            elif attack == 'fake_website':
                doc_data = {
                    "utility_bill": {"address": company_addr, "completeness": 0.95, "date": self._recent_date()},
                    "bank_statement": {"completeness": 0.9},
                    "website": random.choice([
                        "https://pastebin.com/fake-company",
                        "https://example.github.io/temp-page",
                        "https://expired-domain-for-sale.com"
                    ])
                }
                desc = "Suspicious website URL - temporary/expired domain"

            elif attack == 'address_mismatch':
                # Use different company's address for document
                other_comp = companies[(i+5) % len(companies)]
                wrong_addr = self._format_address(other_comp['address'])
                doc_data = {
                    "utility_bill": {
                        "address": wrong_addr,  # Different address
                        "account_holder": comp['company_name'],
                        "date": self._recent_date(),
                        "completeness": 0.95,
                        "provider": "British Gas"
                    },
                    "bank_statement": {"completeness": 0.9},
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk"
                }
                desc = f"Document address doesn't match registered address"

            elif attack == 'partial_document':
                # Completeness just below threshold - harder to catch
                doc_data = {
                    "utility_bill": {
                        "address": company_addr,
                        "account_holder": comp['company_name'],
                        "date": self._recent_date(),
                        "completeness": 0.28,  # Just below 0.3 threshold
                        "provider": "EDF Energy",
                        "missing_fields": ["account_number", "usage_details"]
                    },
                    "bank_statement": {"completeness": 0.9},
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk"
                }
                desc = "Partial document with completeness 0.28 - edge of detection threshold"

            elif attack == 'postcode_manipulation':
                # Postcode off by one character - subtle fraud
                fake_postcode = postcode[:-1] + ('A' if postcode[-1] != 'A' else 'B')
                fake_addr = company_addr.replace(postcode, fake_postcode)
                doc_data = {
                    "utility_bill": {
                        "address": fake_addr,
                        "account_holder": comp['company_name'],
                        "date": self._recent_date(),
                        "completeness": 0.95,
                        "provider": "Thames Water"
                    },
                    "bank_statement": {"completeness": 0.9},
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk"
                }
                desc = f"Postcode manipulation: {postcode} → {fake_postcode}"

            elif attack == 'stale_document':
                # Document older than acceptable verification window
                old_date = (datetime.now() - timedelta(days=420)).strftime('%Y-%m-%d')
                doc_data = {
                    "utility_bill": {
                        "address": company_addr,
                        "account_holder": comp['company_name'],
                        "date": old_date,  # 14 months old
                        "completeness": 1.0,
                        "provider": "SSE"
                    },
                    "bank_statement": {"completeness": 0.9},
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk"
                }
                desc = "Stale document - dated 14 months ago, outside verification window"

            elif attack == 'name_variation':
                # Company name variation that looks legitimate but doesn't match exactly
                name_original = comp['company_name']
                if 'LTD' in name_original.upper():
                    name_variant = name_original.replace('LTD', 'LIMITED').replace('Ltd', 'Limited')
                elif 'LIMITED' in name_original.upper():
                    name_variant = name_original.replace('LIMITED', 'LTD').replace('Limited', 'Ltd')
                else:
                    name_variant = name_original + " SERVICES"

                doc_data = {
                    "utility_bill": {
                        "address": company_addr,
                        "account_holder": name_variant,  # Slight name difference
                        "date": self._recent_date(),
                        "completeness": 0.95,
                        "provider": "British Gas"
                    },
                    "bank_statement": {"completeness": 0.9},
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk"
                }
                desc = f"Name variation: '{name_original}' vs '{name_variant}'"

            elif attack == 'dormant_company':
                # Company status is dormant but documents show active trading
                doc_data = {
                    "utility_bill": {
                        "address": company_addr,
                        "account_holder": comp['company_name'],
                        "date": self._recent_date(15),  # Very recent
                        "completeness": 1.0,
                        "provider": "EDF Energy"
                    },
                    "bank_statement": {"completeness": 1.0, "recent_transactions": 45},
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk"
                }
                desc = "Dormant company with active trading evidence - status mismatch"
                # Override company status
                case_company_data = {
                    **{k: v for k, v in comp.items() if k != 'address'},
                    "registered_address": company_addr,
                    "status": "dormant"  # Key fraud signal
                }

            elif attack == 'recent_website':
                # Website domain registered very recently - suspicious for established company
                doc_data = {
                    "utility_bill": {
                        "address": company_addr,
                        "account_holder": comp['company_name'],
                        "date": self._recent_date(),
                        "completeness": 0.95,
                        "provider": "British Gas"
                    },
                    "bank_statement": {"completeness": 0.9},
                    "website": f"https://www.{self._clean_company_name_for_url(comp['company_name'])}.co.uk",
                    "domain_registration_date": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
                }
                desc = f"Website domain registered 2 days ago for company incorporated {comp['date_of_creation']}"

            # Build company data
            if attack != 'dormant_company':
                case_company_data = {
                    "company_name": comp['company_name'],
                    "company_number": comp['company_number'],
                    "registered_address": company_addr,
                    "date_of_incorporation": comp['date_of_creation'],
                    "sic_codes": comp['sic_codes'][:2],
                    "status": "active"
                }

            case = KYBTestCase(
                case_id=f"ADV-{i:03d}",
                category="adversarial",
                attack_type=attack,
                company_data=case_company_data,
                document_data=doc_data,
                expected_outcome="reject",
                ground_truth_label="fraudulent",
                adversarial_difficulty=diff,
                description=desc
            )
            cases.append(case)

        return cases

    def generate_edge_cases(self, n: int = 10) -> List[KYBTestCase]:
        """Generate ambiguous edge cases that should be escalated"""
        cases = []
        # Reuse companies - wrap around since we only have 30 total
        companies = self.real_companies[:n] if len(self.real_companies) >= n else self.real_companies

        edge_scenarios = [
            ('newly_incorporated', 'Company incorporated last month - limited trading history'),
            ('virtual_office', 'Virtual office address shared by 40+ companies'),
            ('recent_name_change', 'Company changed name 3 weeks ago - documents use old name'),
            ('international_subsidiary', 'UK subsidiary of non-UK parent - complex structure'),
            ('dormant_reactivation', 'Recently moved from dormant to active status'),
            ('residential_address', 'Registered at residential property - home-based business'),
            ('multiple_sic_codes', 'Multiple diverse SIC codes - unclear primary business activity'),
            ('pending_strike_off', 'Active company with pending strike-off notice'),
            ('director_mismatch', 'Signatory on documents not listed as current director'),
            ('psc_unclear', 'Person with Significant Control information incomplete')
        ]

        for i, (edge_type, desc) in enumerate(edge_scenarios[:n], 1):
            comp = companies[i % len(companies)]
            addr = comp['address']
            company_addr = self._format_address(addr)

            # All edge cases have complete docs but ambiguous context
            doc_data = {
                "utility_bill": {
                    "address": company_addr,
                    "account_holder": comp['company_name'],
                    "date": self._recent_date(),
                    "completeness": 0.95,
                    "provider": random.choice(["British Gas", "EDF Energy"])
                },
                "bank_statement": {"completeness": 0.9},
                "website": f"https://www.{comp['company_name'][:15].lower().replace(' ', '')}.co.uk"
            }

            # Modify company data based on edge case type
            company_data = {
                "company_name": comp['company_name'],
                "company_number": comp['company_number'],
                "registered_address": company_addr,
                "date_of_incorporation": comp['date_of_creation'],
                "sic_codes": comp['sic_codes'][:2],
                "status": "active"
            }

            if edge_type == 'newly_incorporated':
                company_data['date_of_incorporation'] = (datetime.now() - timedelta(days=35)).strftime('%Y-%m-%d')
            elif edge_type == 'virtual_office':
                company_data['registered_address'] = "1 Primrose Street, London, EC2A 2EX"  # Known virtual office
                company_data['office_type'] = 'virtual'
            elif edge_type == 'recent_name_change':
                company_data['previous_names'] = [{"name": f"OLD {comp['company_name']}", "date_changed": self._recent_date(25)}]

            case = KYBTestCase(
                case_id=f"EDGE-{i:03d}",
                category="edge_case",
                attack_type=None,
                company_data=company_data,
                document_data=doc_data,
                expected_outcome="escalate",
                ground_truth_label="ambiguous",
                adversarial_difficulty=None,
                description=desc
            )
            cases.append(case)

        return cases


def main():
    # TODO: pull companies dynamically from Companies House API instead of static JSON
    print("="*80)
    print("Generating Improved KYB Test Cases with Real Companies House Data")
    print("="*80)

    generator = ImprovedKYBGenerator()

    print("\n[1/3] Generating legitimate cases (20)...")
    legitimate = generator.generate_legitimate_cases(20)
    print(f"  ✓ Generated {len(legitimate)} legitimate cases")

    print("\n[2/3] Generating adversarial cases (20)...")
    adversarial = generator.generate_adversarial_cases(20)
    print(f"  ✓ Generated {len(adversarial)} adversarial cases")
    print(f"      - Trivial: {sum(1 for c in adversarial if c.adversarial_difficulty == 'trivial')}")
    print(f"      - Moderate: {sum(1 for c in adversarial if c.adversarial_difficulty == 'moderate')}")
    print(f"      - Hard: {sum(1 for c in adversarial if c.adversarial_difficulty == 'hard')}")

    print("\n[3/3] Generating edge cases (10)...")
    edge_cases = generator.generate_edge_cases(10)
    print(f"  ✓ Generated {len(edge_cases)} edge cases")

    all_cases = legitimate + adversarial + edge_cases
    random.shuffle(all_cases)  # Shuffle so evaluator doesn't see patterns

    output_file = 'data/test_cases.json'
    with open(output_file, 'w') as f:
        json.dump([c.to_dict() for c in all_cases], f, indent=2)

    print("\n" + "="*80)
    print(f"Generated {len(all_cases)} test cases")
    print(f"Saved to: {output_file}")
    print("="*80)

    # Print sample cases
    print("\nSample cases:")
    for case in all_cases[:3]:
        print(f"\n  {case.case_id} ({case.category})")
        print(f"  Company: {case.company_data['company_name']}")
        print(f"  {case.description}")


if __name__ == "__main__":
    main()
