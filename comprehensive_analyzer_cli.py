#!/usr/bin/env python3
"""
Comprehensive Analyzer CLI with diagram-ready output formats
Creates unique folders for each GitHub repo analyzed
"""

import json
import sys
import os
from pathlib import Path
from comprehensive_repo_analyzer import ComprehensiveRepoAnalyzer, parse_github_url


def create_repo_folder(owner: str, repo: str) -> str:
    """
    Create a unique folder for the repo analysis.
    Replaces slashes with underscores.

    Examples:
        facebook/react → facebook_react/
        vuejs/vue → vuejs_vue/
        psf/requests → psf_requests/

    Returns:
        Path to the created folder
    """
    folder_name = f"{owner}_{repo}"

    # Create folder if it doesn't exist
    Path(folder_name).mkdir(exist_ok=True)

    return folder_name


def get_output_path(folder: str, filename: str) -> str:
    """Get full path for output file within repo folder"""
    return os.path.join(folder, filename)


class DiagramFormatter:
    """Convert analysis to diagram-friendly formats (color-coded for visualization)"""

    @staticmethod
    def format_for_mermaid(report: dict) -> str:
        """Output as Mermaid diagram (nodes with color coding)"""
        repo = report['repo']
        findings = report['findings']

        # Count by status
        status_map = {
            '✅ GREEN': 'green',
            '⚠️ YELLOW': 'orange',
            '🔴 RED': 'red'
        }

        # Group findings by phase
        phases = {}
        for finding in findings:
            phase = finding['phase']
            if phase not in phases:
                phases[phase] = {'green': 0, 'yellow': 0, 'red': 0}

            status_text = finding['status']
            if 'GREEN' in status_text:
                phases[phase]['green'] += 1
            elif 'YELLOW' in status_text:
                phases[phase]['yellow'] += 1
            elif 'RED' in status_text:
                phases[phase]['red'] += 1

        # Build Mermaid diagram
        mermaid = f"""graph TD
    Repo["📦 {repo}"]

    Phase1["Phase 1: Understanding<br/>✅ {phases.get('1: Understanding', {}).get('green', 0)} 🟡 {phases.get('1: Understanding', {}).get('yellow', 0)} 🔴 {phases.get('1: Understanding', {}).get('red', 0)}"]
    Phase2["Phase 2: Structural<br/>✅ {phases.get('2: Structural', {}).get('green', 0)} 🟡 {phases.get('2: Structural', {}).get('yellow', 0)} 🔴 {phases.get('2: Structural', {}).get('red', 0)}"]
    Phase3["Phase 3: Quality<br/>✅ {phases.get('3: Quality', {}).get('green', 0)} 🟡 {phases.get('3: Quality', {}).get('yellow', 0)} 🔴 {phases.get('3: Quality', {}).get('red', 0)}"]
    Phase4["Phase 4: Security<br/>✅ {phases.get('4: Security', {}).get('green', 0)} 🟡 {phases.get('4: Security', {}).get('yellow', 0)} 🔴 {phases.get('4: Security', {}).get('red', 0)}"]

    Repo --> Phase1
    Repo --> Phase2
    Repo --> Phase3
    Repo --> Phase4

    classDef green fill:#90EE90
    classDef yellow fill:#FFD700
    classDef red fill:#FF6B6B
    classDef neutral fill:#E0E0E0
"""

        return mermaid

    @staticmethod
    def format_for_csv(report: dict) -> str:
        """Output as CSV for spreadsheet analysis"""
        findings = report['findings']

        lines = ["Phase,Status,Title,Location,Impact,Recommendation"]

        for finding in findings:
            # Escape quotes in values
            def escape_csv(val):
                return f'"{str(val).replace(chr(34), chr(34)+chr(34))}"' if val else '""'

            line = ",".join([
                escape_csv(finding['phase']),
                escape_csv(finding['status']),
                escape_csv(finding['title']),
                escape_csv(finding['location']),
                escape_csv(finding['impact']),
                escape_csv(finding['recommendation'])
            ])
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def format_for_json_visualization(report: dict) -> str:
        """Output structured JSON for visualization tools"""
        findings = report['findings']

        # Transform for D3.js or similar visualization
        nodes = []
        links = []

        repo_node = {
            'id': 'repo',
            'label': report['repo'],
            'type': 'repo',
            'status': 'neutral'
        }
        nodes.append(repo_node)

        # Create phase nodes and finding nodes
        phase_ids = set()
        for i, finding in enumerate(findings):
            phase = finding['phase']

            # Add phase node if not exists
            if phase not in phase_ids:
                phase_id = phase.replace(' ', '_').replace(':', '')
                nodes.append({
                    'id': phase_id,
                    'label': phase,
                    'type': 'phase',
                    'status': 'neutral'
                })
                links.append({'source': 'repo', 'target': phase_id})
                phase_ids.add(phase)

            # Add finding node
            finding_id = f"finding_{i}"
            status_map = {
                '✅ GREEN': 'green',
                '⚠️ YELLOW': 'yellow',
                '🔴 RED': 'red'
            }
            status = status_map.get(finding['status'], 'unknown')

            nodes.append({
                'id': finding_id,
                'label': finding['title'][:40],  # Truncate for readability
                'type': 'finding',
                'status': status,
                'full_title': finding['title'],
                'recommendation': finding['recommendation']
            })

            phase_id = phase.replace(' ', '_').replace(':', '')
            links.append({'source': phase_id, 'target': finding_id})

        return json.dumps({
            'nodes': nodes,
            'links': links,
            'summary': report['analysis_summary']
        }, indent=2)

    @staticmethod
    def format_table(report: dict) -> str:
        """Format as human-readable table"""
        findings = report['findings']
        summary = report['analysis_summary']

        output = []
        output.append("\n" + "="*120)
        output.append("COMPREHENSIVE ANALYSIS REPORT")
        output.append("="*120)
        output.append(f"\nRepository: {report['repo']}")
        output.append(f"Total Findings: {summary['total_findings']}")
        output.append(f"  ✅ GREEN (Good): {summary['status_breakdown']['green']}")
        output.append(f"  ⚠️ YELLOW (Needs attention): {summary['status_breakdown']['yellow']}")
        output.append(f"  🔴 RED (Critical): {summary['status_breakdown']['red']}")

        output.append("\n" + "-"*120)
        output.append(f"{'Phase':<20} {'Status':<15} {'Title':<40} {'Location':<20}")
        output.append("-"*120)

        for finding in findings:
            phase = finding['phase'][:19]
            status = finding['status']
            title = finding['title'][:39]
            location = finding['location'][:19]

            output.append(f"{phase:<20} {status:<15} {title:<40} {location:<20}")

        # Detailed findings
        output.append("\n" + "="*120)
        output.append("DETAILED FINDINGS")
        output.append("="*120)

        for i, finding in enumerate(findings, 1):
            output.append(f"\n{i}. {finding['status']} {finding['title']}")
            output.append(f"   Phase: {finding['phase']}")
            output.append(f"   Location: {finding['location']}")
            output.append(f"   Impact: {finding['impact']}")
            output.append(f"   Recommendation: {finding['recommendation']}")

        # Critical actions
        critical = report.get('critical_actions', [])
        if critical:
            output.append("\n" + "="*120)
            output.append("CRITICAL ACTION ITEMS")
            output.append("="*120)

            for action in critical:
                output.append(f"\n[{action['priority']}] {action['finding']}")
                output.append(f"  Action: {action['action']}")

        output.append("\n" + "="*120 + "\n")
        return "\n".join(output)


def show_format_menu():
    """Display format selection menu"""
    print("\n📊 Select output format:")
    print("  1. Table (human-readable) - DEFAULT")
    print("  2. JSON (structured data)")
    print("  3. CSV (spreadsheet analysis)")
    print("  4. Mermaid (diagram syntax)")
    print("  5. D3 (visualization data)")
    print("  6. All formats (generate all 5)")

    while True:
        choice = input("\nEnter choice (1-6) [default: 1]: ").strip() or "1"
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        print("❌ Invalid choice. Please enter 1-6.")


def format_choice_to_format_name(choice: str) -> list:
    """Convert menu choice to format name(s)"""
    format_map = {
        '1': ['table'],
        '2': ['json'],
        '3': ['csv'],
        '4': ['mermaid'],
        '5': ['d3json'],
        '6': ['table', 'json', 'csv', 'mermaid', 'd3json']
    }
    return format_map.get(choice, ['table'])


def generate_output(report: dict, output_format: str) -> str:
    """Generate output in specified format"""
    if output_format == 'json':
        return json.dumps(report, indent=2)
    elif output_format == 'mermaid':
        return DiagramFormatter.format_for_mermaid(report)
    elif output_format == 'csv':
        return DiagramFormatter.format_for_csv(report)
    elif output_format == 'd3json':
        return DiagramFormatter.format_for_json_visualization(report)
    else:  # table (default)
        return DiagramFormatter.format_table(report)


def get_filename(repo: str, output_format: str) -> str:
    """Get filename for format"""
    filename_map = {
        'json': f"{repo}_analysis.json",
        'mermaid': f"{repo}_diagram.md",
        'csv': f"{repo}_findings.csv",
        'd3json': f"{repo}_visualization.json",
        'table': f"{repo}_report.txt"
    }
    return filename_map.get(output_format, f"{repo}_report.txt")


def main():
    print("\n" + "="*70)
    print("🔍 COMPREHENSIVE REPOSITORY ANALYZER")
    print("="*70)

    # Get GitHub repo URL from user
    print("\nEnter the GitHub repository URL:")
    print("  Examples: facebook/react")
    print("           https://github.com/vuejs/vue")
    print("           psf/requests")

    while True:
        repo_input = input("\n📦 GitHub repo URL: ").strip()

        if not repo_input:
            print("❌ Please enter a GitHub repo URL")
            continue

        # Validate format
        if not ('/' in repo_input or repo_input.startswith('http')):
            print("❌ Invalid format. Use 'owner/repo' or full GitHub URL")
            continue

        break

    # Get output format preference
    format_choice = show_format_menu()
    output_formats = format_choice_to_format_name(format_choice)

    # Check for command-line format override
    if '--format' in sys.argv:
        idx = sys.argv.index('--format')
        if idx + 1 < len(sys.argv):
            output_formats = [sys.argv[idx + 1]]

    try:
        owner, repo = parse_github_url(repo_input)

        print(f"\n🔍 Analyzing {owner}/{repo}...")
        print("This may take 10-30 seconds...\n")

        # Create unique folder for this repo
        repo_folder = create_repo_folder(owner, repo)
        print(f"📁 Created analysis folder: {repo_folder}/\n")

        analyzer = ComprehensiveRepoAnalyzer(owner, repo)
        report = analyzer.generate_report()

        # Generate output in selected format(s)
        for output_format in output_formats:
            print(f"📋 Generating {output_format.upper()} output...")

            output = generate_output(report, output_format)
            filename = get_filename(repo, output_format)
            filepath = get_output_path(repo_folder, filename)

            # Print to console (full output for first format, summary for others)
            if output_format == output_formats[0]:
                print(output)
            else:
                print(f"✅ {output_format.upper()} output generated")

            # Save to file in repo folder
            with open(filepath, 'w') as f:
                f.write(output)

            print(f"✅ Saved to: {filepath}\n")

        print("="*70)
        print("✨ Analysis complete!")
        print("="*70)

        # Show summary
        summary = report['analysis_summary']
        print(f"\n📊 Summary:")
        print(f"   Total findings: {summary['total_findings']}")
        print(f"   ✅ GREEN: {summary['status_breakdown']['green']}")
        print(f"   ⚠️ YELLOW: {summary['status_breakdown']['yellow']}")
        print(f"   🔴 RED: {summary['status_breakdown']['red']}")

        print(f"\n📁 All files saved to: {os.path.abspath(repo_folder)}/\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Analysis cancelled by user")
        sys.exit(0)
