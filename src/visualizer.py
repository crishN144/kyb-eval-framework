"""
KYB Adversarial Evaluation Console v3 - Production Grade

Premium dark AI evaluation console for KYB compliance systems.
Refined for production use by YC startups and research teams.
"""

import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List
import random


class ProductionEvaluationConsole:
    """Production-grade AI evaluation console"""

    # Premium dark palette
    COLORS = {
        'bg_page': '#0d1117',           # Deep charcoal
        'bg_card': '#161b22',           # Card surface
        'bg_header': '#0d1117',         # Header (same as page)
        'border': '#30363d',            # Subtle borders
        'border_glow': '#58a6ff',       # Accent glow
        'primary': '#7c3aed',           # Violet-blue
        'success': '#10b981',           # Muted emerald
        'warning': '#f59e0b',           # Amber
        'danger': '#f97316',            # Coral-red
        'info': '#3b82f6',              # Blue
        'text': '#e6edf3',              # Cool off-white
        'text_muted': '#7d8590',        # Muted gray
        'text_subtle': '#484f58',       # Subtle gray
    }

    def __init__(self, test_cases: List[Dict], metrics: Dict, results: List):
        self.test_cases = test_cases
        self.metrics = metrics
        self.results = results

    def create_key_findings(self) -> str:
        """Key findings insight strip"""
        dom_metrics = self.metrics['domain_specific_metrics']
        failure_analysis = self.metrics.get('failure_analysis', {})

        # Determine findings
        findings = []

        # Finding 1: Adversarial performance
        adv_rate = dom_metrics['adversarial_rejection_rate']
        if adv_rate == 1.0:
            findings.append({
                'icon': '✓',
                'text': 'All adversarial cases blocked',
                'status': 'excellent'
            })
        elif adv_rate >= 0.8:
            findings.append({
                'icon': '!',
                'text': f'{int(adv_rate * 100)}% adversarial blocked',
                'status': 'good'
            })
        else:
            findings.append({
                'icon': '⚠',
                'text': f'{int(adv_rate * 100)}% adversarial blocked',
                'status': 'warning'
            })

        # Finding 2: Main weakness
        edge_rate = dom_metrics['edge_case_escalation_rate']
        if edge_rate < 0.8:
            findings.append({
                'icon': '→',
                'text': 'Edge cases remain the weakest path',
                'status': 'watch'
            })

        # Finding 3: False positives/escalations
        fp_rate = dom_metrics['false_positive_rate']
        leg_approve_rate = dom_metrics['legitimate_approval_rate']
        if leg_approve_rate < 1.0:
            # Some legitimate cases were not approved (either rejected or escalated)
            leg_total = self.metrics['test_case_counts']['legitimate']
            not_approved = int((1 - leg_approve_rate) * leg_total)
            findings.append({
                'icon': '!',
                'text': f'{not_approved} legitimate case{"s" if not_approved != 1 else ""} wrongly escalated',
                'status': 'watch'
            })

        # Finding 4: Perfect recall
        fn_rate = dom_metrics['false_negative_rate']
        if fn_rate == 0:
            findings.append({
                'icon': '✓',
                'text': 'Zero fraudulent cases slipped through',
                'status': 'excellent'
            })

        html = '<div class="findings-strip">'

        for finding in findings[:3]:  # Max 3 findings
            status_class = {
                'excellent': 'finding-excellent',
                'good': 'finding-good',
                'watch': 'finding-watch',
                'warning': 'finding-warning'
            }.get(finding['status'], 'finding-good')

            html += f"""
            <div class="finding-pill {status_class}">
                <span class="finding-icon">{finding['icon']}</span>
                <span class="finding-text">{finding['text']}</span>
            </div>
            """

        html += '</div>'
        return html

    def create_metric_cards_v3(self) -> str:
        """Production metric cards with status indicators"""
        std_metrics = self.metrics['standard_metrics']
        dom_metrics = self.metrics['domain_specific_metrics']

        def get_status(value, thresholds):
            """Determine status based on value"""
            if value >= thresholds['excellent']:
                return 'excellent', '✓ Excellent'
            elif value >= thresholds['good']:
                return 'good', '✓ Good'
            elif value >= thresholds['fair']:
                return 'fair', '→ Fair'
            else:
                return 'needs-review', '⚠ Needs review'

        cards_data = [
            {
                'label': 'Overall Accuracy',
                'value': std_metrics['overall_accuracy'],
                'sublabel': f"{int(std_metrics['overall_accuracy'] * len(self.test_cases))}/{len(self.test_cases)} cases correct",
                'thresholds': {'excellent': 0.9, 'good': 0.8, 'fair': 0.7},
                'color': 'primary'
            },
            {
                'label': 'Adversarial Rejection',
                'value': dom_metrics['adversarial_rejection_rate'],
                'sublabel': f"{int(dom_metrics['adversarial_rejection_rate'] * self.metrics['test_case_counts']['adversarial'])}/{self.metrics['test_case_counts']['adversarial']} fraud-like cases blocked",
                'thresholds': {'excellent': 0.95, 'good': 0.85, 'fair': 0.75},
                'color': 'success'
            },
            {
                'label': 'Legitimate Approval',
                'value': dom_metrics['legitimate_approval_rate'],
                'sublabel': f"{int(dom_metrics['legitimate_approval_rate'] * self.metrics['test_case_counts']['legitimate'])}/{self.metrics['test_case_counts']['legitimate']} valid businesses approved",
                'thresholds': {'excellent': 0.9, 'good': 0.8, 'fair': 0.7},
                'color': 'info'
            },
            {
                'label': 'Edge Case Escalation',
                'value': dom_metrics['edge_case_escalation_rate'],
                'sublabel': f"{int(dom_metrics['edge_case_escalation_rate'] * self.metrics['test_case_counts']['edge_cases'])}/{self.metrics['test_case_counts']['edge_cases']} ambiguous cases sent for review",
                'thresholds': {'excellent': 0.85, 'good': 0.7, 'fair': 0.5},
                'color': 'warning'
            },
            {
                'label': 'False Positive Rate',
                'value': dom_metrics['false_positive_rate'],
                'sublabel': 'legitimate cases wrongly rejected',
                'thresholds': {'excellent': 0.95, 'good': 0.90, 'fair': 0.85},
                'color': 'danger',
                'invert': True  # Lower is better
            },
            {
                'label': 'False Negative Rate',
                'value': dom_metrics['false_negative_rate'],
                'sublabel': 'fraudulent cases that slipped through',
                'thresholds': {'excellent': 1.0, 'good': 0.95, 'fair': 0.90},
                'color': 'danger',
                'invert': True
            }
        ]

        html = '<div class="metrics-grid-v3">'

        for card in cards_data:
            # Adjust thresholds if inverted (lower is better)
            if card.get('invert'):
                status, status_text = get_status(
                    1 - card['value'],  # Invert
                    card['thresholds']
                )
            else:
                status, status_text = get_status(card['value'], card['thresholds'])

            html += f"""
            <div class="metric-card-v3 metric-{card['color']}">
                <div class="metric-header">
                    <span class="metric-label-v3">{card['label']}</span>
                    <span class="metric-status status-{status}">{status_text}</span>
                </div>
                <div class="metric-value-v3">{card['value'] * 100:.1f}%</div>
                <div class="metric-sublabel-v3">{card['sublabel']}</div>
                <div class="metric-progress">
                    <div class="metric-progress-bar" style="width: {card['value'] * 100}%"></div>
                </div>
            </div>
            """

        html += '</div>'
        return html

    def create_sankey_v3(self) -> go.Figure:
        """Polished Sankey with clean labels"""
        flows = {}

        for i, case in enumerate(self.test_cases):
            result = self.results[i] if i < len(self.results) else None
            if not result:
                continue

            category = case.get('category', 'unknown').replace('_', ' ').title()
            expected = case.get('expected_outcome', 'unknown').title()
            predicted = result.predicted.title() if result else 'Unknown'
            outcome = 'Pass' if (result and result.correct) else 'Fail'

            flow_key = f"{category}→{expected}→{predicted}→{outcome}"
            flows[flow_key] = flows.get(flow_key, 0) + 1

        # Build nodes
        nodes = []
        node_map = {}

        def get_node_index(label, stage):
            if label not in node_map:
                node_map[label] = len(nodes)

                # Color by stage and type
                color = self.COLORS['text_muted']
                if 'Adversarial' in label:
                    color = self.COLORS['danger']
                elif 'Legitimate' in label:
                    color = self.COLORS['success']
                elif 'Edge' in label:
                    color = self.COLORS['warning']
                elif 'Pass' in label:
                    color = self.COLORS['success']
                elif 'Fail' in label:
                    color = self.COLORS['danger']
                elif 'Expected' in label or 'Predicted' in label:
                    color = self.COLORS['info']

                nodes.append({'label': label, 'color': color})
            return node_map[label]

        sources, targets, values, colors = [], [], [], []

        for flow_key, count in flows.items():
            parts = flow_key.split('→')
            if len(parts) == 4:
                cat, exp, pred, outcome = parts

                # Category → Expected
                sources.append(get_node_index(cat, 'cat'))
                targets.append(get_node_index(f"Expected: {exp}", 'exp'))
                values.append(count)
                colors.append('rgba(124, 58, 237, 0.2)')

                # Expected → Predicted
                sources.append(get_node_index(f"Expected: {exp}", 'exp'))
                targets.append(get_node_index(f"Predicted: {pred}", 'pred'))
                values.append(count)
                colors.append('rgba(59, 130, 246, 0.2)')

                # Predicted → Outcome
                sources.append(get_node_index(f"Predicted: {pred}", 'pred'))
                targets.append(get_node_index(outcome, 'outcome'))
                values.append(count)
                if outcome == 'Pass':
                    colors.append('rgba(16, 185, 129, 0.25)')
                else:
                    colors.append('rgba(249, 115, 22, 0.25)')

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=18,
                line=dict(color=self.COLORS['border'], width=1),
                label=[n['label'] for n in nodes],
                color=[n['color'] for n in nodes],
                hovertemplate='%{label}<br>Cases: %{value}<extra></extra>',
                customdata=[n['label'] for n in nodes]
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors,
                hovertemplate='%{source.label} → %{target.label}<br>Count: %{value}<extra></extra>'
            )
        )])

        fig.update_layout(
            template=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Inter, sans-serif",
                size=11,
                color="#E6EDF3"
            ),
            hoverlabel=dict(
                bgcolor="rgba(18,22,28,0.92)",
                bordercolor="rgba(255,255,255,0.08)",
                font=dict(
                    family="Inter, sans-serif",
                    size=12,
                    color="#E6EDF3"
                )
            ),
            height=450,
            margin=dict(l=24, r=24, t=20, b=24),
            hovermode="closest"
        )

        return fig

    def create_case_galaxy_v3(self) -> go.Figure:
        """Refined scatter with better axis naming and filters"""
        case_data = []
        difficulty_map = {'trivial': 1, 'moderate': 2, 'hard': 3, None: 1.5}

        for i, case in enumerate(self.test_cases):
            result = self.results[i] if i < len(self.results) else None
            if not result:
                continue

            category = case.get('category', 'unknown')
            attack_type = case.get('attack_type', 'none')
            difficulty = case.get('adversarial_difficulty')

            # X: Case Complexity
            x_val = difficulty_map.get(difficulty, 1.5) + random.uniform(-0.12, 0.12)

            # Y: Verification Risk
            if category == 'adversarial':
                base_risk = 3.0
            elif category == 'edge_case':
                base_risk = 2.0
            else:
                base_risk = 1.0

            if result and not result.correct:
                base_risk += 0.8

            y_val = base_risk + random.uniform(-0.15, 0.15)

            color = self.COLORS['success']
            if category == 'adversarial':
                color = self.COLORS['danger']
            elif category == 'edge_case':
                color = self.COLORS['warning']

            symbol = 'circle' if (result and result.correct) else 'x'

            case_data.append({
                'case_id': case.get('case_id', 'N/A'),
                'category': category.replace('_', ' ').title(),
                'attack_type': attack_type.replace('_', ' ').title() if (attack_type and attack_type != 'none') else 'N/A',
                'complexity': x_val,
                'risk': y_val,
                'color': color,
                'symbol': symbol,
                'status': 'Pass' if (result and result.correct) else 'Fail',
                'predicted': result.predicted.title() if result else 'N/A'
            })

        df = pd.DataFrame(case_data)

        fig = go.Figure()

        for category in ['Legitimate', 'Adversarial', 'Edge Case']:
            cat_df = df[df['category'] == category]

            for status in ['Pass', 'Fail']:
                status_df = cat_df[cat_df['status'] == status]
                if len(status_df) == 0:
                    continue

                fig.add_trace(go.Scatter(
                    x=status_df['complexity'],
                    y=status_df['risk'],
                    mode='markers',
                    name=f"{category} ({status})",
                    marker=dict(
                        size=10,
                        color=status_df['color'].iloc[0],
                        symbol='circle' if status == 'Pass' else 'x',
                        line=dict(width=1, color=self.COLORS['border']),
                        opacity=0.8
                    ),
                    text=status_df.apply(lambda row:
                        f"<b>{row['case_id']}</b><br>"
                        f"Category: {row['category']}<br>"
                        f"Attack: {row['attack_type']}<br>"
                        f"Predicted: {row['predicted']}<br>"
                        f"Status: {row['status']}",
                        axis=1
                    ),
                    hovertemplate='%{text}<extra></extra>'
                ))

        fig.update_layout(
            xaxis=dict(
                title=dict(
                    text='<b>Case Complexity</b>',
                    font=dict(size=12)
                ),
                tickvals=[1, 2, 3],
                ticktext=['Low', 'Medium', 'High'],
                gridcolor=self.COLORS['border'],
                gridwidth=0.5,
                color=self.COLORS['text'],
                showline=False,
                zeroline=False
            ),
            yaxis=dict(
                title=dict(
                    text='<b>Verification Risk</b>',
                    font=dict(size=12)
                ),
                gridcolor=self.COLORS['border'],
                gridwidth=0.5,
                color=self.COLORS['text'],
                showline=False,
                zeroline=False
            ),
            plot_bgcolor=self.COLORS['bg_card'],
            paper_bgcolor=self.COLORS['bg_card'],
            font=dict(color=self.COLORS['text'], family='Inter', size=11),
            height=450,
            showlegend=True,
            legend=dict(
                bgcolor=self.COLORS['bg_page'],
                bordercolor=self.COLORS['border'],
                borderwidth=1,
                font=dict(size=10)
            ),
            margin=dict(l=60, r=20, t=20, b=60),
            hovermode='closest'
        )

        return fig

    def create_attack_robustness_strip(self) -> str:
        """Simple editorial attack pattern summary"""
        # Analyze performance by attack type
        attack_performance = {}

        for i, case in enumerate(self.test_cases):
            result = self.results[i] if i < len(self.results) else None
            if not result:
                continue

            attack_type = case.get('attack_type', 'none')
            if attack_type == 'none' or not attack_type:
                continue

            if attack_type not in attack_performance:
                attack_performance[attack_type] = {'total': 0, 'blocked': 0}

            attack_performance[attack_type]['total'] += 1
            if result.predicted in ['reject', 'fraudulent']:
                attack_performance[attack_type]['blocked'] += 1

        if not attack_performance:
            return ''

        # Categorize attacks as robust (100% blocked) or vulnerable (<100%)
        robust = []
        vulnerable = []

        for attack_type, stats in attack_performance.items():
            attack_label = attack_type.replace('_', ' ').title()
            if stats['blocked'] == stats['total']:
                robust.append(attack_label)
            else:
                vulnerable.append(attack_label)

        # Build inline lists with middot separators
        robust_list = ' · '.join(robust) if robust else 'None'
        vulnerable_list = ' · '.join(vulnerable) if vulnerable else 'None'

        return f"""
        <div class="attack-patterns">
            <p class="attack-summary">Most structural attacks are blocked consistently. Failures cluster around timeliness, naming variation, and business-state checks.</p>

            <div class="pattern-group">
                <div class="pattern-label">Robust against</div>
                <div class="pattern-list">{robust_list}</div>
            </div>

            <div class="pattern-group">
                <div class="pattern-label pattern-label-vulnerable">Still vulnerable to</div>
                <div class="pattern-list">{vulnerable_list}</div>
            </div>
        </div>
        """

    def create_confusion_matrix_heatmap(self) -> go.Figure:
        """3x3 confusion matrix heatmap with color coding"""
        confusion = self.metrics.get('confusion_matrix', {})

        # Define label order
        labels = ['legitimate', 'fraudulent', 'ambiguous']
        label_display = ['Legitimate', 'Fraudulent', 'Ambiguous']

        # Build matrix
        matrix = []
        for actual_label in labels:
            row = []
            for pred_label in labels:
                count = confusion.get(actual_label, {}).get(pred_label, 0)
                row.append(count)
            matrix.append(row)

        # Color scale: diagonal (correct) = green, off-diagonal (errors) = orange/red
        text_values = [[str(val) for val in row] for row in matrix]

        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=label_display,
            y=label_display,
            text=text_values,
            texttemplate='<b>%{text}</b>',
            textfont={"size": 16, "color": "white"},
            colorscale=[
                [0.0, self.COLORS['bg_page']],      # 0 cases = dark
                [0.3, self.COLORS['danger']],        # Few cases = red (errors)
                [0.6, self.COLORS['warning']],       # Medium = orange
                [1.0, self.COLORS['success']]        # Many = green (correct)
            ],
            showscale=False,
            hovertemplate='Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>'
        ))

        fig.update_layout(
            template=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=dict(text='<b>Predicted Label</b>', font=dict(size=12)),
                side='bottom',
                color="#E6EDF3",
                showgrid=False,
                showline=False
            ),
            yaxis=dict(
                title=dict(text='<b>Actual Label</b>', font=dict(size=12)),
                autorange='reversed',
                color="#E6EDF3",
                showgrid=False,
                showline=False
            ),
            font=dict(color="#E6EDF3", family='Inter, sans-serif', size=11),
            hoverlabel=dict(
                bgcolor="rgba(18,22,28,0.92)",
                bordercolor="rgba(255,255,255,0.08)",
                font=dict(family="Inter, sans-serif", size=12, color="#E6EDF3")
            ),
            height=350,
            margin=dict(l=80, r=20, t=20, b=80),
            hovermode="closest"
        )

        return fig

    def create_failure_mode_bar_chart(self) -> go.Figure:
        """Horizontal bar chart showing failure breakdown by type"""
        failure_analysis = self.metrics.get('failure_analysis', {})
        failure_counts = failure_analysis.get('failure_counts', {})

        if not failure_counts:
            # Return empty figure
            fig = go.Figure()
            fig.update_layout(
                plot_bgcolor=self.COLORS['bg_card'],
                paper_bgcolor=self.COLORS['bg_card'],
                height=300
            )
            return fig

        # Sort by count descending
        sorted_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)

        labels = [item[0].replace('_', ' ').title() for item in sorted_failures]
        values = [item[1] for item in sorted_failures]

        # Color based on failure type
        colors = []
        for label, _ in sorted_failures:
            if 'edge_case' in label.lower():
                colors.append(self.COLORS['warning'])
            elif 'false_negative' in label.lower():
                colors.append(self.COLORS['danger'])
            elif 'false_positive' in label.lower():
                colors.append(self.COLORS['info'])
            else:
                colors.append(self.COLORS['text_muted'])

        fig = go.Figure(data=[go.Bar(
            x=values,
            y=labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color=self.COLORS['border'], width=1)
            ),
            text=values,
            textposition='outside',
            textfont=dict(size=12, color=self.COLORS['text'], family='JetBrains Mono'),
            hovertemplate='<b>%{y}</b><br>Failures: %{x}<extra></extra>'
        )])

        fig.update_layout(
            template=None,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=dict(text='<b>Number of Failures</b>', font=dict(size=12)),
                gridcolor="rgba(255,255,255,0.05)",
                gridwidth=0.5,
                color="#E6EDF3",
                showline=False,
                zeroline=True
            ),
            yaxis=dict(
                color="#E6EDF3",
                showgrid=False,
                showline=False,
                autorange='reversed'
            ),
            font=dict(color="#E6EDF3", family='Inter, sans-serif', size=11),
            hoverlabel=dict(
                bgcolor="rgba(18,22,28,0.92)",
                bordercolor="rgba(255,255,255,0.08)",
                font=dict(family="Inter, sans-serif", size=12, color="#E6EDF3")
            ),
            height=max(280, len(labels) * 45),
            margin=dict(l=200, r=60, t=20, b=60),
            showlegend=False,
            hovermode="closest"
        )

        return fig

    def create_case_cards_v3(self) -> str:
        """Refined case cards with better filters"""
        # Group by category
        categories = {}
        for i, case in enumerate(self.test_cases):
            result = self.results[i] if i < len(self.results) else None
            if not result:
                continue

            category = case.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append((case, result))

        html = []
        html.append('<div class="case-explorer-v3">')

        # Filter pills
        html.append('<div class="case-filters">')
        html.append('<span class="filter-label">Filter:</span>')
        html.append('<button class="filter-pill filter-active" data-category="all">All Cases</button>')
        html.append('<button class="filter-pill" data-category="legitimate">Legitimate</button>')
        html.append('<button class="filter-pill" data-category="adversarial">Adversarial</button>')
        html.append('<button class="filter-pill" data-category="edge_case">Edge Cases</button>')
        html.append('</div>')

        # Cards
        html.append('<div class="case-cards-grid">')

        for category, items in categories.items():
            for case, result in items:
                case_id = case.get('case_id', 'N/A')
                attack_type = case.get('attack_type', 'N/A') or 'N/A'
                expected = case.get('expected_outcome', 'N/A')
                predicted = result.predicted if result else 'N/A'
                status = 'pass' if (result and result.correct) else 'fail'

                category_class = {
                    'legitimate': 'category-success',
                    'adversarial': 'category-danger',
                    'edge_case': 'category-warning'
                }.get(category, 'category-info')

                status_class = 'status-pass' if status == 'pass' else 'status-fail'
                status_icon = '✓' if status == 'pass' else '✗'

                html.append(f"""
                <div class="case-card-v3 {status_class}" data-category="{category}">
                    <div class="case-card-header-v3">
                        <code class="case-id-v3">{case_id}</code>
                        <span class="case-status-badge {status_class}">{status_icon}</span>
                    </div>
                    <div class="case-card-body-v3">
                        <div class="case-row">
                            <span class="case-key">Category</span>
                            <span class="case-badge {category_class}">{category.replace('_', ' ').title()}</span>
                        </div>
                        <div class="case-row">
                            <span class="case-key">Attack</span>
                            <span class="case-value">{attack_type.replace('_', ' ').title()}</span>
                        </div>
                        <div class="case-row">
                            <span class="case-key">Expected</span>
                            <span class="case-value">{expected.title()}</span>
                        </div>
                        <div class="case-row">
                            <span class="case-key">Predicted</span>
                            <span class="case-value">{predicted.title()}</span>
                        </div>
                    </div>
                </div>
                """)

        html.append('</div>')
        html.append('</div>')

        return '\n'.join(html)

    def generate_production_console(self, output_path: str = "results/kyb_evaluation_console.html"):
        """Generate production-grade evaluation console"""
        print("\n" + "=" * 80)
        print("🚀 Generating Production KYB Evaluation Console v3")
        print("=" * 80)

        print("\n[1/5] Creating key findings strip...")
        findings_html = self.create_key_findings()

        print("[2/5] Creating production metric cards...")
        metric_cards_html = self.create_metric_cards_v3()

        print("[3/5] Creating polished Sankey flow...")
        sankey_fig = self.create_sankey_v3()

        print("[4/5] Creating attack robustness strip...")
        robustness_html = self.create_attack_robustness_strip()

        # Convert Plotly figures to HTML before f-string
        sankey_html = sankey_fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False})

        print("[5/5] Creating refined case explorer...")
        case_cards_html = self.create_case_cards_v3()

        print("\nCombining into premium glass console...")

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KYB Adversarial Evaluation Console</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --ease-premium: cubic-bezier(0.22, 1, 0.36, 1);
            --motion-fast: 180ms var(--ease-premium);
            --motion-med: 220ms var(--ease-premium);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: {self.COLORS['bg_page']};
            color: {self.COLORS['text']};
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}

        /* ===== HEADER ===== */
        .console-header {{
            background:
                radial-gradient(circle at 15% 0%, rgba(124,58,237,0.10), transparent 35%),
                radial-gradient(circle at 85% 0%, rgba(59,130,246,0.08), transparent 30%),
                linear-gradient(180deg, rgba(16,18,24,0.96), rgba(13,17,23,0.88));
            backdrop-filter: blur(18px) saturate(130%);
            -webkit-backdrop-filter: blur(18px) saturate(130%);
            border-bottom: 1px solid rgba(255,255,255,0.07);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 10px 30px rgba(0,0,0,0.2);
            padding: 24px 32px;
            position: relative;
        }}

        .console-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(
                90deg,
                rgba(124,58,237,0.00),
                rgba(124,58,237,0.55),
                rgba(59,130,246,0.55),
                rgba(124,58,237,0.00)
            );
            opacity: 0.8;
        }}

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .console-title {{
            font-size: 22px;
            font-weight: 600;
            letter-spacing: -0.03em;
            margin-bottom: 4px;
        }}

        .console-subtitle {{
            font-size: 13px;
            color: rgba(230,237,243,0.62);
            margin-bottom: 16px;
            font-weight: 400;
        }}

        .console-meta {{
            display: flex;
            gap: 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: {self.COLORS['text_subtle']};
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .meta-value {{
            color: {self.COLORS['text_muted']};
            font-weight: 500;
        }}

        /* ===== KEY FINDINGS ===== */
        .findings-strip {{
            max-width: 1400px;
            margin: 24px auto;
            padding: 0 32px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .finding-pill {{
            background: linear-gradient(
                180deg,
                rgba(22, 27, 34, 0.84) 0%,
                rgba(18, 22, 28, 0.76) 100%
            );
            backdrop-filter: blur(14px) saturate(135%);
            -webkit-backdrop-filter: blur(14px) saturate(135%);
            border: 1px solid rgba(255,255,255,0.07);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 8px 24px rgba(0,0,0,0.18);
            border-radius: 8px;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 13px;
            transition:
                transform var(--motion-med),
                box-shadow var(--motion-med),
                border-color var(--motion-med),
                background var(--motion-med),
                opacity var(--motion-med);
            position: relative;
            overflow: hidden;
        }}

        .finding-pill::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                135deg,
                rgba(255,255,255,0.06) 0%,
                rgba(255,255,255,0.02) 18%,
                rgba(255,255,255,0.00) 40%
            );
            opacity: 0.55;
            pointer-events: none;
        }}

        .finding-pill:hover {{
            transform: translateY(-3px) scale(1.005);
            border-color: rgba(124,58,237,0.22);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.05),
                0 14px 28px rgba(0,0,0,0.24),
                0 0 0 1px rgba(124,58,237,0.04);
        }}

        .finding-excellent {{
            border-left: 3px solid {self.COLORS['success']};
        }}

        .finding-good {{
            border-left: 3px solid {self.COLORS['info']};
        }}

        .finding-watch {{
            border-left: 3px solid {self.COLORS['warning']};
        }}

        .finding-warning {{
            border-left: 3px solid {self.COLORS['danger']};
        }}

        .finding-icon {{
            font-size: 14px;
            opacity: 0.8;
        }}

        .finding-text {{
            font-weight: 500;
        }}

        /* ===== CONTAINER ===== */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 32px 40px;
        }}

        .section {{
            background: linear-gradient(
                180deg,
                rgba(22, 27, 34, 0.84) 0%,
                rgba(18, 22, 28, 0.76) 100%
            );
            backdrop-filter: blur(14px) saturate(135%);
            -webkit-backdrop-filter: blur(14px) saturate(135%);
            border: 1px solid rgba(255,255,255,0.07);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 8px 24px rgba(0,0,0,0.18);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            transition:
                transform var(--motion-med),
                box-shadow var(--motion-med),
                border-color var(--motion-med),
                background var(--motion-med),
                opacity var(--motion-med);
            overflow: hidden;
            position: relative;
        }}

        .section::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                135deg,
                rgba(255,255,255,0.06) 0%,
                rgba(255,255,255,0.02) 18%,
                rgba(255,255,255,0.00) 40%
            );
            opacity: 0.55;
            pointer-events: none;
        }}

        .section:hover {{
            transform: translateY(-3px) scale(1.005);
            border-color: rgba(124,58,237,0.22);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.05),
                0 14px 28px rgba(0,0,0,0.24),
                0 0 0 1px rgba(124,58,237,0.04);
        }}

        .section-header {{
            margin-bottom: 20px;
        }}

        .section-title {{
            font-size: 17px;
            font-weight: 600;
            margin-bottom: 4px;
            letter-spacing: -0.02em;
        }}

        .section-subtitle {{
            font-size: 12px;
            color: rgba(230,237,243,0.52);
            font-weight: 400;
        }}

        /* ===== METRIC CARDS V3 ===== */
        .metrics-grid-v3 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .metric-card-v3 {{
            background: linear-gradient(
                180deg,
                rgba(22, 27, 34, 0.84) 0%,
                rgba(18, 22, 28, 0.76) 100%
            );
            backdrop-filter: blur(14px) saturate(135%);
            -webkit-backdrop-filter: blur(14px) saturate(135%);
            border: 1px solid rgba(255,255,255,0.07);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 8px 24px rgba(0,0,0,0.18);
            border-radius: 12px;
            padding: 18px;
            transition:
                transform var(--motion-med),
                box-shadow var(--motion-med),
                border-color var(--motion-med),
                background var(--motion-med),
                opacity var(--motion-med);
            position: relative;
            overflow: hidden;
        }}

        .metric-card-v3::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            border-radius: 12px 12px 0 0;
            opacity: 0;
            transition: opacity var(--motion-med);
        }}

        .metric-card-v3::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                135deg,
                rgba(255,255,255,0.06) 0%,
                rgba(255,255,255,0.02) 18%,
                rgba(255,255,255,0.00) 40%
            );
            opacity: 0.55;
            pointer-events: none;
        }}

        .metric-card-v3:hover {{
            transform: translateY(-3px) scale(1.005);
            border-color: rgba(124,58,237,0.22);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.05),
                0 14px 28px rgba(0,0,0,0.24),
                0 0 0 1px rgba(124,58,237,0.04);
        }}

        .metric-card-v3:hover::before {{
            opacity: 1;
        }}

        .metric-primary::before {{ background: {self.COLORS['primary']}; }}
        .metric-success::before {{ background: {self.COLORS['success']}; }}
        .metric-info::before {{ background: {self.COLORS['info']}; }}
        .metric-warning::before {{ background: {self.COLORS['warning']}; }}
        .metric-danger::before {{ background: {self.COLORS['danger']}; }}

        .metric-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }}

        .metric-label-v3 {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: {self.COLORS['text_muted']};
            font-weight: 500;
        }}

        .metric-status {{
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 500;
            font-family: 'JetBrains Mono', monospace;
        }}

        .status-excellent {{
            background: rgba(16, 185, 129, 0.12);
            color: {self.COLORS['success']};
            border: 1px solid rgba(16, 185, 129, 0.25);
        }}

        .status-good {{
            background: rgba(59, 130, 246, 0.12);
            color: {self.COLORS['info']};
            border: 1px solid rgba(59, 130, 246, 0.25);
        }}

        .status-fair {{
            background: rgba(245, 158, 11, 0.12);
            color: {self.COLORS['warning']};
            border: 1px solid rgba(245, 158, 11, 0.25);
        }}

        .status-needs-review {{
            background: rgba(249, 115, 22, 0.12);
            color: {self.COLORS['danger']};
            border: 1px solid rgba(249, 115, 22, 0.25);
        }}

        .metric-value-v3 {{
            font-size: 32px;
            font-weight: 700;
            color: {self.COLORS['text']};
            font-family: 'JetBrains Mono', monospace;
            line-height: 1;
            margin-bottom: 8px;
        }}

        .metric-sublabel-v3 {{
            font-size: 11px;
            color: {self.COLORS['text_subtle']};
            margin-bottom: 10px;
        }}

        .metric-progress {{
            height: 3px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 2px;
            overflow: hidden;
        }}

        .metric-progress-bar {{
            height: 100%;
            background: {self.COLORS['border_glow']};
            border-radius: 2px;
            transition: width 0.6s ease;
        }}

        /* ===== ATTACK ROBUSTNESS STRIP ===== */
        .robustness-strip {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
            margin-bottom: 24px;
        }}

        .robustness-tile {{
            background: linear-gradient(
                180deg,
                rgba(22, 27, 34, 0.84) 0%,
                rgba(18, 22, 28, 0.76) 100%
            );
            backdrop-filter: blur(14px) saturate(135%);
            -webkit-backdrop-filter: blur(14px) saturate(135%);
            border: 1px solid rgba(255,255,255,0.07);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 8px 24px rgba(0,0,0,0.18);
            border-radius: 8px;
            padding: 14px;
            transition:
                transform var(--motion-med),
                box-shadow var(--motion-med),
                border-color var(--motion-med),
                background var(--motion-med),
                opacity var(--motion-med);
            position: relative;
            overflow: hidden;
        }}

        .robustness-tile::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                135deg,
                rgba(255,255,255,0.06) 0%,
                rgba(255,255,255,0.02) 18%,
                rgba(255,255,255,0.00) 40%
            );
            opacity: 0.55;
            pointer-events: none;
        }}

        .robustness-tile:hover {{
            transform: translateY(-3px) scale(1.005);
            border-color: rgba(124,58,237,0.22);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.05),
                0 14px 28px rgba(0,0,0,0.24),
                0 0 0 1px rgba(124,58,237,0.04);
        }}

        .robustness-excellent {{
            border-left: 3px solid {self.COLORS['success']};
        }}

        .robustness-good {{
            border-left: 3px solid {self.COLORS['info']};
        }}

        .robustness-warning {{
            border-left: 3px solid {self.COLORS['danger']};
        }}

        .robustness-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}

        .robustness-icon {{
            font-size: 12px;
            opacity: 0.8;
        }}

        .robustness-label {{
            font-size: 11px;
            font-weight: 500;
            color: {self.COLORS['text_muted']};
        }}

        .robustness-value {{
            font-size: 24px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 4px;
        }}

        .robustness-count {{
            font-size: 10px;
            color: {self.COLORS['text_subtle']};
            margin-bottom: 8px;
        }}

        .robustness-bar {{
            height: 3px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 2px;
            overflow: hidden;
        }}

        .robustness-bar-fill {{
            height: 100%;
            background: {self.COLORS['border_glow']};
            border-radius: 2px;
        }}

        /* ===== CASE EXPLORER V3 ===== */
        .case-filters {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .filter-label {{
            font-size: 12px;
            color: {self.COLORS['text_muted']};
            font-weight: 500;
            margin-right: 4px;
        }}

        .filter-pill {{
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(14px) saturate(135%);
            -webkit-backdrop-filter: blur(14px) saturate(135%);
            border: 1px solid rgba(255,255,255,0.07);
            color: {self.COLORS['text_muted']};
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition:
                transform var(--motion-med),
                background var(--motion-med),
                border-color var(--motion-med),
                box-shadow var(--motion-med),
                color var(--motion-med);
        }}

        .filter-pill:hover {{
            transform: translateY(-2px) scale(1.005);
            border-color: rgba(124,58,237,0.22);
            background: rgba(124,58,237,0.08);
            box-shadow:
                0 8px 18px rgba(0,0,0,0.18),
                0 0 0 1px rgba(124,58,237,0.04);
            color: {self.COLORS['text']};
        }}

        .filter-active {{
            background: linear-gradient(
                180deg,
                rgba(124,58,237,0.90),
                rgba(99,102,241,0.82)
            );
            border-color: rgba(255,255,255,0.10);
            color: #fff;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.10),
                0 8px 18px rgba(124,58,237,0.22);
        }}

        .case-cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 14px;
            max-height: 500px;
            overflow-y: auto;
            padding-right: 8px;
        }}

        .case-cards-grid::-webkit-scrollbar {{
            width: 6px;
        }}

        .case-cards-grid::-webkit-scrollbar-track {{
            background: {self.COLORS['bg_page']};
            border-radius: 3px;
        }}

        .case-cards-grid::-webkit-scrollbar-thumb {{
            background: {self.COLORS['border']};
            border-radius: 3px;
        }}

        .case-card-v3 {{
            background: linear-gradient(
                180deg,
                rgba(13, 17, 23, 0.84) 0%,
                rgba(10, 14, 19, 0.76) 100%
            );
            backdrop-filter: blur(14px) saturate(135%);
            -webkit-backdrop-filter: blur(14px) saturate(135%);
            border: 1px solid rgba(255,255,255,0.07);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.04),
                0 8px 24px rgba(0,0,0,0.18);
            border-radius: 8px;
            padding: 14px;
            transition:
                transform var(--motion-med),
                box-shadow var(--motion-med),
                border-color var(--motion-med),
                background var(--motion-med),
                opacity var(--motion-med);
            position: relative;
            overflow: hidden;
        }}

        .case-card-v3::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                135deg,
                rgba(255,255,255,0.04) 0%,
                rgba(255,255,255,0.01) 18%,
                rgba(255,255,255,0.00) 40%
            );
            opacity: 0.55;
            pointer-events: none;
        }}

        .case-card-v3:hover {{
            transform: translateY(-3px) scale(1.005);
            border-color: rgba(124,58,237,0.22);
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.05),
                0 14px 28px rgba(0,0,0,0.24),
                0 0 0 1px rgba(124,58,237,0.04);
        }}

        .status-pass {{
            border-left: 3px solid {self.COLORS['success']};
        }}

        .status-fail {{
            border-left: 3px solid {self.COLORS['danger']};
        }}

        .case-card-header-v3 {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid {self.COLORS['border']};
        }}

        .case-id-v3 {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            font-weight: 600;
            color: {self.COLORS['text']};
        }}

        .case-status-badge {{
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }}

        .case-status-badge.status-pass {{
            background: rgba(16, 185, 129, 0.12);
            color: {self.COLORS['success']};
            border: 1px solid rgba(16, 185, 129, 0.25);
            border-left-width: 1px;
        }}

        .case-status-badge.status-fail {{
            background: rgba(249, 115, 22, 0.12);
            color: {self.COLORS['danger']};
            border: 1px solid rgba(249, 115, 22, 0.25);
            border-left-width: 1px;
        }}

        .case-card-body-v3 {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .case-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }}

        .case-key {{
            color: {self.COLORS['text_subtle']};
            font-weight: 500;
        }}

        .case-value {{
            color: {self.COLORS['text_muted']};
            font-weight: 500;
        }}

        .case-badge {{
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 500;
        }}

        .category-success {{
            background: rgba(16, 185, 129, 0.12);
            color: {self.COLORS['success']};
            border: 1px solid rgba(16, 185, 129, 0.25);
        }}

        .category-danger {{
            background: rgba(249, 115, 22, 0.12);
            color: {self.COLORS['danger']};
            border: 1px solid rgba(249, 115, 22, 0.25);
        }}

        .category-warning {{
            background: rgba(245, 158, 11, 0.12);
            color: {self.COLORS['warning']};
            border: 1px solid rgba(245, 158, 11, 0.25);
        }}

        /* ===== ATTACK PATTERNS ===== */
        .attack-patterns {{
            padding: 0;
        }}

        .attack-summary {{
            font-size: 14px;
            color: {self.COLORS['text']};
            line-height: 1.6;
            margin: 0 0 20px 0;
        }}

        .pattern-group {{
            margin-bottom: 16px;
        }}

        .pattern-label {{
            font-size: 12px;
            font-weight: 600;
            color: {self.COLORS['success']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .pattern-label-vulnerable {{
            color: {self.COLORS['warning']};
        }}

        .pattern-list {{
            font-size: 13px;
            color: {self.COLORS['text_muted']};
            line-height: 1.8;
        }}

        /* ===== FOOTER ===== */
        .footer {{
            text-align: center;
            padding: 20px;
            color: rgba(230,237,243,0.32);
            font-size: 11px;
            margin-top: 40px;
        }}

        .footer a {{
            color: rgba(230,237,243,0.42);
            text-decoration: none;
        }}

        .footer a:hover {{
            color: {self.COLORS['primary']};
        }}
    </style>
</head>
<body>
    <!-- HEADER -->
    <div class="console-header">
        <div class="header-content">
            <h1 class="console-title">KYB Adversarial Evaluation Console</h1>
            <p class="console-subtitle">Interactive robustness analysis for KYB verification systems</p>
            <div class="console-meta">
                <div class="meta-item">
                    <span>Cases:</span>
                    <span class="meta-value">{len(self.test_cases)}</span>
                </div>
                <div class="meta-item">
                    <span>Accuracy:</span>
                    <span class="meta-value">{self.metrics['standard_metrics']['overall_accuracy'] * 100:.1f}%</span>
                </div>
                <div class="meta-item">
                    <span>Framework:</span>
                    <span class="meta-value">arXiv:2601.14479</span>
                </div>
            </div>
        </div>
    </div>

    <!-- KEY FINDINGS -->
    {findings_html}

    <!-- MAIN CONTAINER -->
    <div class="container">
        <!-- METRIC CARDS -->
        {metric_cards_html}

        <!-- DECISION FLOW -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Decision Flow</h2>
                <p class="section-subtitle">How cases move from input category through expected action to final decision. Most adversarial cases resolve correctly; edge cases create the main friction.</p>
            </div>
            {sankey_html}
        </div>

        <!-- ATTACK PATTERNS -->
        {f'<div class="section"><div class="section-header"><h2 class="section-title">Attack patterns</h2></div>{robustness_html}</div>' if robustness_html else ''}

        <!-- CASE EXPLORER -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Case Explorer</h2>
                <p class="section-subtitle">Individual test cases with expected vs actual outcomes.</p>
            </div>
            {case_cards_html}
        </div>
    </div>

    <script>
        // Simple filter functionality
        document.querySelectorAll('.filter-pill').forEach(pill => {{
            pill.addEventListener('click', () => {{
                // Update active state
                document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('filter-active'));
                pill.classList.add('filter-active');

                // Filter cards
                const category = pill.dataset.category;
                document.querySelectorAll('.case-card-v3').forEach(card => {{
                    if (category === 'all' || card.dataset.category === category) {{
                        card.style.display = 'block';
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        file_size_kb = len(html_content) / 1024
        print(f"\n✅ Premium Glass Console Generated!")
        print(f"   📁 Path: {output_path}")
        print(f"   📦 Size: {file_size_kb:.1f} KB")
        print(f"   🎨 Style: Soft Glass Surfaces with Depth-Shift Hover")
        print(f"   📊 Sections: 5 (Header + Findings + Metrics + Decision Flow + Attack Robustness + Case Explorer)")
        print("\n" + "=" * 80)

        return output_path


def main():
    """Generate production evaluation console"""
    import argparse
    import sys
    sys.path.insert(0, '.')

    from evaluator import KYBEvaluationFramework

    parser = argparse.ArgumentParser(description="Generate production KYB evaluation console")
    parser.add_argument("--test-cases", default="data/test_cases.json",
                       help="Path to test cases JSON")
    parser.add_argument("--output", default="results/kyb_evaluation_console.html",
                       help="Output HTML path")

    args = parser.parse_args()

    print(f"Loading test cases from: {args.test_cases}")
    with open(args.test_cases, 'r') as f:
        test_cases = json.load(f)

    print(f"Loaded {len(test_cases)} test cases\n")
    print("Running evaluation...")
    framework = KYBEvaluationFramework(test_cases)
    metrics = framework.run_evaluation()

    console = ProductionEvaluationConsole(test_cases, metrics, framework.results)
    output_path = console.generate_production_console(args.output)

    print(f"\n🎉 Open {output_path} in your browser!")


if __name__ == "__main__":
    main()
