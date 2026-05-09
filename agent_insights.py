#!/usr/bin/env python3
"""
Agent Insights Engine
Extracts patterns, insights, and generates actionable recommendations from analysis
"""

from typing import Dict, List, Optional
from collections import defaultdict


class InsightExtractor:
    """Extract meaningful insights from analysis findings"""

    def __init__(self, report: Dict):
        self.report = report
        self.findings = report['findings']
        self.summary = report['analysis_summary']

    def extract(self) -> Dict:
        """Extract all insights from the analysis"""
        return {
            'top_insights': self._top_insights(),
            'phase_health': self._phase_health(),
            'status_distribution': self._status_distribution(),
            'critical_gaps': self._critical_gaps(),
            'patterns': self._identify_patterns()
        }

    def _top_insights(self) -> List[str]:
        """Generate high-level insights"""
        insights = []

        # Overall health
        total = self.summary['total_findings']
        critical = self.summary['status_breakdown']['red']
        good = self.summary['status_breakdown']['green']

        health_pct = (good / total * 100) if total > 0 else 0
        if health_pct > 70:
            insights.append(f"Overall codebase health is STRONG ({health_pct:.0f}% good)")
        elif health_pct > 40:
            insights.append(f"Codebase is STABLE but needs attention ({health_pct:.0f}% good)")
        else:
            insights.append(f"Codebase has SIGNIFICANT issues ({health_pct:.0f}% good)")

        # Critical issues
        if critical > 0:
            insights.append(f"{critical} CRITICAL issues require immediate attention")

        # Phase distribution
        phase_findings = self._findings_by_phase()
        worst_phase = max(phase_findings, key=lambda x: len(phase_findings[x]))
        best_phase = min(phase_findings, key=lambda x: len(phase_findings[x]))
        insights.append(f"Weakest area: {worst_phase} ({len(phase_findings[worst_phase])} issues)")
        insights.append(f"Strongest area: {best_phase} ({len(phase_findings[best_phase])} issues)")

        # Testing status
        testing_findings = [f for f in self.findings if 'test' in f['title'].lower()]
        if testing_findings:
            test_status = [f for f in testing_findings if '🔴 RED' in f['status']]
            if test_status:
                insights.append("⚠️ TESTING: No automated test configuration found - HIGH PRIORITY")

        # Security status
        security_findings = [f for f in self.findings if f['phase'] == '4: Security']
        security_critical = [f for f in security_findings if '🔴 RED' in f['status']]
        security_yellow = [f for f in security_findings if '⚠️ YELLOW' in f['status']]
        if security_yellow or security_critical:
            insights.append(f"🔐 SECURITY: {len(security_critical)} critical, {len(security_yellow)} warnings")

        return insights

    def _phase_health(self) -> Dict[str, Dict]:
        """Analyze health by phase"""
        phase_data = defaultdict(lambda: {'total': 0, 'green': 0, 'yellow': 0, 'red': 0})

        for finding in self.findings:
            phase = finding['phase']
            phase_data[phase]['total'] += 1

            if '✅ GREEN' in finding['status']:
                phase_data[phase]['green'] += 1
            elif '⚠️ YELLOW' in finding['status']:
                phase_data[phase]['yellow'] += 1
            elif '🔴 RED' in finding['status']:
                phase_data[phase]['red'] += 1

        return dict(phase_data)

    def _status_distribution(self) -> Dict[str, int]:
        """Get count by status"""
        return self.summary['status_breakdown']

    def _critical_gaps(self) -> List[Dict]:
        """Identify critical capability gaps"""
        gaps = []

        # Check for missing testing
        testing_red = [f for f in self.findings if 'test' in f['title'].lower() and '🔴 RED' in f['status']]
        if testing_red:
            gaps.append({
                'area': 'Testing',
                'severity': 'CRITICAL',
                'impact': 'No automated tests increases bug risk and deployment risk',
                'examples': [f['title'] for f in testing_red[:2]]
            })

        # Check for missing security
        security_red = [f for f in self.findings if f['phase'] == '4: Security' and '🔴 RED' in f['status']]
        if security_red:
            gaps.append({
                'area': 'Security',
                'severity': 'CRITICAL',
                'impact': 'Security vulnerabilities may go undetected',
                'examples': [f['title'] for f in security_red[:2]]
            })

        # Check for missing configuration
        config_issues = [f for f in self.findings if 'config' in f['title'].lower() and '⚠️ YELLOW' in f['status']]
        if len(config_issues) > 2:
            gaps.append({
                'area': 'Configuration Management',
                'severity': 'HIGH',
                'impact': 'Inconsistent configuration may lead to deployment issues',
                'examples': [f['title'] for f in config_issues[:2]]
            })

        return gaps

    def _identify_patterns(self) -> List[str]:
        """Identify patterns in findings"""
        patterns = []

        # Count issues by type
        issue_types = defaultdict(int)
        for finding in self.findings:
            title = finding['title'].lower()
            if 'dependency' in title or 'package' in title or 'framework' in title:
                issue_types['dependency_management'] += 1
            elif 'style' in title or 'config' in title or 'lint' in title:
                issue_types['code_standards'] += 1
            elif 'test' in title:
                issue_types['testing'] += 1
            elif 'security' in title or 'scanning' in title:
                issue_types['security'] += 1
            elif 'document' in title or 'readme' in title:
                issue_types['documentation'] += 1

        # Report patterns
        if issue_types['dependency_management'] > 1:
            patterns.append(f"Dependency management needs attention ({issue_types['dependency_management']} issues)")

        if issue_types['code_standards'] > 2:
            patterns.append(f"Code standardization is a concern ({issue_types['code_standards']} issues)")

        if issue_types['testing'] > 0:
            patterns.append("Testing infrastructure gaps detected")

        if issue_types['security'] > 1:
            patterns.append(f"Security practices need strengthening ({issue_types['security']} issues)")

        if issue_types['documentation'] > 0 and \
           any('document' in f['title'].lower() and '✅ GREEN' in f['status'] for f in self.findings):
            patterns.append("Good documentation baseline exists - leverage it")

        return patterns if patterns else ["No specific patterns identified - issues are distributed"]

    def _findings_by_phase(self) -> Dict[str, List]:
        """Group findings by phase"""
        by_phase = defaultdict(list)
        for finding in self.findings:
            by_phase[finding['phase']].append(finding)
        return by_phase


class RecommendationEngine:
    """Generate actionable recommendations based on findings"""

    def __init__(self, report: Dict, insights: Dict):
        self.report = report
        self.insights = insights
        self.findings = report['findings']

    def generate(self) -> List[Dict]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Critical recommendations (RED findings)
        recommendations.extend(self._critical_recommendations())

        # High-priority recommendations (YELLOW findings that are high-impact)
        recommendations.extend(self._high_priority_recommendations())

        # Medium recommendations (quick wins)
        recommendations.extend(self._medium_priority_recommendations())

        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 999))

        return recommendations

    def _critical_recommendations(self) -> List[Dict]:
        """Generate critical recommendations from RED findings"""
        recommendations = []

        for finding in self.findings:
            if '🔴 RED' not in finding['status']:
                continue

            title = finding['title'].lower()
            phase = finding['phase']

            # Testing recommendation
            if 'test' in title:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'title': 'Implement Automated Testing',
                    'action': finding['recommendation'],
                    'impact': 'Reduces bug risk by 70%, enables safe refactoring',
                    'effort': 'medium',
                    'finding': finding['title']
                })

            # Security recommendation
            elif 'security' in title or 'scanning' in title:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'title': 'Enable Security Scanning',
                    'action': finding['recommendation'],
                    'impact': 'Detects vulnerabilities before production',
                    'effort': 'low',
                    'finding': finding['title']
                })

            # General RED finding
            else:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'title': finding['title'],
                    'action': finding['recommendation'],
                    'impact': finding['impact'],
                    'effort': 'medium',
                    'finding': finding['title']
                })

        return recommendations

    def _high_priority_recommendations(self) -> List[Dict]:
        """Generate high-priority recommendations"""
        recommendations = []

        for finding in self.findings:
            if '⚠️ YELLOW' not in finding['status']:
                continue

            title = finding['title'].lower()
            phase = finding['phase']

            # High-impact yellow findings
            if 'organization' in title or 'structure' in title:
                recommendations.append({
                    'priority': 'HIGH',
                    'title': 'Improve Code Organization',
                    'action': finding['recommendation'],
                    'impact': 'Improves maintainability and reduces bugs',
                    'effort': 'medium',
                    'finding': finding['title']
                })

            elif 'dependency' in title:
                recommendations.append({
                    'priority': 'HIGH',
                    'title': 'Manage Dependencies',
                    'action': finding['recommendation'],
                    'impact': 'Reduces security risk and version conflicts',
                    'effort': 'low',
                    'finding': finding['title']
                })

            elif 'style' in title or 'lint' in title:
                recommendations.append({
                    'priority': 'HIGH',
                    'title': 'Add Code Style Configuration',
                    'action': finding['recommendation'],
                    'impact': 'Ensures consistent code quality across team',
                    'effort': 'low',
                    'finding': finding['title']
                })

            elif 'security' in title:
                recommendations.append({
                    'priority': 'HIGH',
                    'title': finding['title'],
                    'action': finding['recommendation'],
                    'impact': 'Strengthens security posture',
                    'effort': 'low',
                    'finding': finding['title']
                })

        return recommendations

    def _medium_priority_recommendations(self) -> List[Dict]:
        """Generate medium-priority (quick win) recommendations"""
        recommendations = []

        for finding in self.findings:
            if '⚠️ YELLOW' not in finding['status']:
                continue

            title = finding['title'].lower()

            # Quick wins with low effort
            if 'environment' in title or 'env' in title:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'title': 'Create Environment Configuration',
                    'action': 'Add .env.example file with template variables',
                    'impact': 'Prevents accidental credential commits',
                    'effort': 'low',
                    'finding': finding['title']
                })

            elif any(word in title for word in ['large file', 'size', '> 10kb']):
                recommendations.append({
                    'priority': 'MEDIUM',
                    'title': 'Refactor Large Files',
                    'action': finding['recommendation'],
                    'impact': 'Improves code readability and testability',
                    'effort': 'medium',
                    'finding': finding['title']
                })

        return recommendations
