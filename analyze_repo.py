#!/usr/bin/env python3
"""
Simple CLI to analyze GitHub repos
Usage: python analyze_repo.py owner/repo
       python analyze_repo.py https://github.com/owner/repo
"""

import sys
import json
from github_repo_analyzer import GitHubRepoAnalyzer, parse_github_url


def pretty_print_analysis(analysis: dict):
    """Pretty print analysis results"""
    if 'error' in analysis:
        print(f"❌ Error: {analysis['error']}")
        return

    print("\n" + "="*80)
    print(f"📊 GITHUB REPOSITORY ANALYSIS")
    print("="*80)

    repo = analysis['repo']
    print(f"\n📦 Repository: {repo}")
    if analysis.get('url'):
        print(f"   URL: {analysis['url']}")
    if analysis.get('description'):
        print(f"   Description: {analysis['description']}")

    # File Analysis
    print(f"\n🔍 FILE ANALYSIS")
    print("-" * 80)
    file_dist = analysis['file_analysis']['language_distribution']
    if file_dist:
        print("   Language Distribution:")
        total_files = sum(file_dist.values())
        for lang, count in list(file_dist.items())[:5]:
            percentage = (count / total_files * 100) if total_files > 0 else 0
            bar = "█" * int(percentage / 5)
            print(f"     {lang:.<30} {count:>4} files ({percentage:>5.1f}%) {bar}")
    else:
        print("   No file distribution data available")

    # Config Analysis
    config = analysis['config_analysis']
    print(f"\n⚙️  TECH STACK DETECTION")
    print("-" * 80)

    if config['frameworks']:
        print(f"   Frameworks: {', '.join(config['frameworks'])}")
    else:
        print("   Frameworks: None detected")

    if config['build_tools']:
        print(f"   Build Tools: {', '.join(config['build_tools'])}")
    else:
        print("   Build Tools: None detected")

    if config['config_files']:
        print(f"   Config Files Found: {', '.join(config['config_files'])}")
    else:
        print("   Config Files: None detected")

    # Summary
    print(f"\n📈 SUMMARY")
    print("-" * 80)
    if analysis.get('summary'):
        print(f"   {analysis['summary']}")

    if analysis.get('primary_language'):
        print(f"   Primary Language (GitHub): {analysis['primary_language']}")

    print("\n" + "="*80 + "\n")


def export_json(analysis: dict, filename: str = None):
    """Export analysis to JSON file"""
    if not filename:
        repo = analysis.get('repo', 'analysis').replace('/', '_')
        filename = f"{repo}_analysis.json"

    with open(filename, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"✅ Results saved to: {filename}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python analyze_repo.py owner/repo")
        print("  python analyze_repo.py https://github.com/owner/repo")
        print("\nExamples:")
        print("  python analyze_repo.py psf/requests")
        print("  python analyze_repo.py torvalds/linux")
        print("  python analyze_repo.py facebook/react")
        sys.exit(1)

    repo_input = sys.argv[1]
    export = '--export' in sys.argv or '-e' in sys.argv

    try:
        owner, repo = parse_github_url(repo_input)
        print(f"\n🔄 Analyzing {owner}/{repo}...")

        analyzer = GitHubRepoAnalyzer(owner, repo)
        analysis = analyzer.analyze()

        pretty_print_analysis(analysis)

        if export:
            export_json(analysis)

    except ValueError as e:
        print(f"❌ Invalid GitHub URL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
