#!/usr/bin/env python3
"""
Repository Analyzer Agent
Orchestrates comprehensive analysis → visualization → insights → recommendations

Workflow:
  1. User provides GitHub repo URL
  2. Agent analyzes repository (4-phase analysis)
  3. Agent generates all output formats
  4. Agent creates interactive visualization
  5. Agent extracts insights and critical findings
  6. Agent presents decision points to user
  7. Agent makes actionable recommendations
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from comprehensive_repo_analyzer import ComprehensiveRepoAnalyzer, parse_github_url
from comprehensive_analyzer_cli import DiagramFormatter, create_repo_folder, get_output_path
from agent_insights import InsightExtractor, RecommendationEngine


class RepositoryAnalyzerAgent:
    """Intelligent agent that orchestrates repository analysis workflow"""

    def __init__(self, github_url: str):
        self.github_url = github_url
        self.owner, self.repo = parse_github_url(github_url)
        self.repo_name = f"{self.owner}_{self.repo}"
        self.repo_folder = create_repo_folder(self.owner, self.repo)
        self.report: Optional[Dict] = None
        self.visualizations = {}

    def print_header(self, text: str, char: str = "="):
        """Pretty print section headers"""
        width = 70
        print(f"\n{char * width}")
        print(f"  {text}")
        print(f"{char * width}\n")

    def analyze_repository(self) -> Dict:
        """Step 1: Analyze repository using comprehensive analyzer"""
        self.print_header("📊 STEP 1: ANALYZING REPOSITORY", "🔍")
        print(f"Repository: {self.owner}/{self.repo}")
        print(f"This may take 10-30 seconds...\n")

        analyzer = ComprehensiveRepoAnalyzer(self.owner, self.repo)
        self.report = analyzer.generate_report()

        # Display summary
        summary = self.report['analysis_summary']
        print(f"✅ Analysis complete!")
        print(f"\n📊 Summary:")
        print(f"   Total findings: {summary['total_findings']}")
        print(f"   ✅ GREEN (Good): {summary['status_breakdown']['green']}")
        print(f"   ⚠️ YELLOW (Needs attention): {summary['status_breakdown']['yellow']}")
        print(f"   🔴 RED (Critical): {summary['status_breakdown']['red']}")

        return self.report

    def generate_visualizations(self) -> Dict[str, str]:
        """Step 2: Generate all visualization formats"""
        self.print_header("📈 STEP 2: GENERATING VISUALIZATIONS", "📊")

        outputs = {}

        # Generate JSON visualization (for interactive graph)
        json_viz = DiagramFormatter.format_for_json_visualization(self.report)
        json_path = get_output_path(self.repo_folder, f"{self.repo_name}_visualization.json")
        with open(json_path, 'w') as f:
            f.write(json_viz)
        outputs['visualization_json'] = json_path
        print(f"✅ Interactive graph data: {json_path}")

        # Generate Mermaid diagram
        mermaid = DiagramFormatter.format_for_mermaid(self.report)
        mermaid_path = get_output_path(self.repo_folder, f"{self.repo_name}_diagram.md")
        with open(mermaid_path, 'w') as f:
            f.write(mermaid)
        outputs['mermaid'] = mermaid_path
        print(f"✅ Mermaid diagram: {mermaid_path}")

        # Generate CSV findings
        csv = DiagramFormatter.format_for_csv(self.report)
        csv_path = get_output_path(self.repo_folder, f"{self.repo_name}_findings.csv")
        with open(csv_path, 'w') as f:
            f.write(csv)
        outputs['csv'] = csv_path
        print(f"✅ CSV findings: {csv_path}")

        # Generate full analysis JSON
        json_path = get_output_path(self.repo_folder, f"{self.repo_name}_analysis.json")
        with open(json_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        outputs['analysis_json'] = json_path
        print(f"✅ Full analysis: {json_path}")

        self.visualizations = outputs
        return outputs

    def extract_insights(self) -> Dict:
        """Step 3: Extract insights and patterns from findings"""
        self.print_header("💡 STEP 3: EXTRACTING INSIGHTS", "🔬")

        extractor = InsightExtractor(self.report)
        insights = extractor.extract()

        print("🎯 KEY INSIGHTS:\n")
        for insight in insights['top_insights']:
            print(f"  • {insight}")

        return insights

    def generate_recommendations(self, insights: Dict) -> List[Dict]:
        """Step 4: Generate actionable recommendations"""
        self.print_header("🎯 STEP 4: GENERATING RECOMMENDATIONS", "📋")

        engine = RecommendationEngine(self.report, insights)
        recommendations = engine.generate()

        # Display recommendations by priority
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM']:
            items = [r for r in recommendations if r['priority'] == priority]
            if items:
                print(f"\n[{priority}]")
                for rec in items:
                    print(f"  • {rec['title']}")
                    print(f"    Action: {rec['action']}")
                    print(f"    Impact: {rec['impact']}\n")

        return recommendations

    def present_decision_points(self, insights: Dict, recommendations: List[Dict]) -> Dict:
        """Step 5: Present interactive decision points to user"""
        self.print_header("🤔 STEP 5: DECISION POINTS", "❓")

        decisions = {}

        # Critical findings decision
        critical_findings = [f for f in self.report['findings'] if '🔴 RED' in f['status']]
        if critical_findings:
            print(f"\n[DECISION 1] You have {len(critical_findings)} CRITICAL findings:")
            for f in critical_findings[:3]:
                print(f"  • {f['title']}")

            choice = input("\n  Would you like a detailed security report? (yes/no) [default: yes]: ").strip().lower()
            decisions['security_report'] = choice != 'no'

        # Phase focus decision
        phases_with_issues = {}
        for finding in self.report['findings']:
            phase = finding['phase']
            phases_with_issues[phase] = phases_with_issues.get(phase, 0) + 1

        worst_phase = max(phases_with_issues, key=phases_with_issues.get)
        print(f"\n[DECISION 2] Phase with most findings: {worst_phase} ({phases_with_issues[worst_phase]} issues)")
        choice = input(f"  Focus on {worst_phase} first? (yes/no) [default: yes]: ").strip().lower()
        decisions['focus_phase'] = worst_phase if choice != 'no' else None

        # Timeline decision
        print(f"\n[DECISION 3] Quick wins vs comprehensive fixes?")
        print(f"  1. Quick wins (fix 3-5 high-impact issues in <1 hour)")
        print(f"  2. Comprehensive (plan full roadmap for 2-4 weeks)")
        choice = input("  Enter choice (1-2) [default: 1]: ").strip() or "1"
        decisions['approach'] = 'quick_wins' if choice == '1' else 'comprehensive'

        return decisions

    def generate_action_plan(self, recommendations: List[Dict], decisions: Dict) -> str:
        """Step 6: Generate personalized action plan"""
        self.print_header("📝 STEP 6: PERSONALIZED ACTION PLAN", "📅")

        # Filter recommendations based on decisions
        if decisions.get('approach') == 'quick_wins':
            relevant_recs = [r for r in recommendations if r['priority'] in ['CRITICAL', 'HIGH'] and r.get('effort') == 'low'][:5]
        else:
            relevant_recs = recommendations

        plan = {
            'approach': decisions.get('approach'),
            'focus_phase': decisions.get('focus_phase'),
            'action_items': []
        }

        print(f"\nApproach: {decisions.get('approach').replace('_', ' ').title()}")
        if decisions.get('focus_phase'):
            print(f"Focus Phase: {decisions.get('focus_phase')}")

        print(f"\nACTION PLAN ({len(relevant_recs)} items):\n")

        for i, rec in enumerate(relevant_recs, 1):
            print(f"{i}. [{rec['priority']}] {rec['title']}")
            print(f"   Action: {rec['action']}")
            print(f"   Expected Impact: {rec['impact']}")
            print()

            plan['action_items'].append({
                'order': i,
                'priority': rec['priority'],
                'title': rec['title'],
                'action': rec['action'],
                'impact': rec['impact']
            })

        return plan

    def save_agent_report(self, insights: Dict, recommendations: List[Dict], decisions: Dict, plan: Dict):
        """Save comprehensive agent report"""
        agent_report = {
            'repository': f"{self.owner}/{self.repo}",
            'analysis_summary': self.report['analysis_summary'],
            'insights': insights,
            'recommendations': recommendations,
            'user_decisions': decisions,
            'action_plan': plan,
            'generated_files': {
                'visualization': self.visualizations.get('visualization_json'),
                'analysis': self.visualizations.get('analysis_json'),
                'csv': self.visualizations.get('csv'),
                'mermaid': self.visualizations.get('mermaid')
            }
        }

        report_path = get_output_path(self.repo_folder, f"{self.repo_name}_agent_report.json")
        with open(report_path, 'w') as f:
            json.dump(agent_report, f, indent=2)

        return report_path

    def run(self):
        """Execute the complete agent workflow"""
        print("\n" + "=" * 70)
        print("  🤖 REPOSITORY ANALYZER AGENT")
        print("  Intelligent Analysis → Insights → Recommendations")
        print("=" * 70)

        try:
            # Step 1: Analyze
            self.analyze_repository()

            # Step 2: Visualize
            self.generate_visualizations()

            # Step 3: Extract insights
            insights = self.extract_insights()

            # Step 4: Generate recommendations
            recommendations = self.generate_recommendations(insights)

            # Step 5: Decision points
            decisions = self.present_decision_points(insights, recommendations)

            # Step 6: Action plan
            plan = self.generate_action_plan(recommendations, decisions)

            # Step 7: Save report
            report_path = self.save_agent_report(insights, recommendations, decisions, plan)

            # Summary
            self.print_header("✨ AGENT WORKFLOW COMPLETE", "🎉")
            print(f"📁 All files saved to: {Path(self.repo_folder).absolute()}/\n")
            print(f"Key files generated:")
            print(f"  • Agent report: {report_path}")
            print(f"  • Interactive graph: {self.visualizations.get('visualization_json')}")
            print(f"  • Analysis data: {self.visualizations.get('analysis_json')}")
            print(f"  • CSV findings: {self.visualizations.get('csv')}")
            print(f"\n✅ Next steps:")
            print(f"  1. Review action plan above")
            print(f"  2. Run: python3 visualize_mike_analysis.py {self.visualizations.get('visualization_json')} {self.repo_folder}")
            print(f"  3. Share results with your team\n")

        except Exception as e:
            print(f"\n❌ Agent error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    print("\n" + "=" * 70)
    print("🤖 REPOSITORY ANALYZER AGENT")
    print("=" * 70)

    print("\nEnter GitHub repository URL:")
    print("  Examples: facebook/react")
    print("           https://github.com/vuejs/vue")
    print("           psf/requests")

    while True:
        repo_input = input("\n📦 GitHub repo URL: ").strip()

        if not repo_input:
            print("❌ Please enter a GitHub repo URL")
            continue

        if not ('/' in repo_input or repo_input.startswith('http')):
            print("❌ Invalid format. Use 'owner/repo' or full GitHub URL")
            continue

        break

    # Create and run agent
    agent = RepositoryAnalyzerAgent(repo_input)
    agent.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Agent workflow cancelled by user")
        sys.exit(0)
