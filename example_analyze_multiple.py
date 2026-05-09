#!/usr/bin/env python3
"""
Example: Analyze multiple popular GitHub repos to demonstrate the analyzer

This shows how you'd scan your organization's repos to build a database
of tech stacks before enforcing UI component standardization
"""

from github_repo_analyzer import GitHubRepoAnalyzer
import json


def analyze_repos(repos: list) -> dict:
    """
    Analyze multiple repos and aggregate results

    Args:
        repos: List of "owner/repo" strings

    Returns:
        Dictionary with all analysis results
    """
    results = {}

    for repo in repos:
        owner, name = repo.split('/')
        print(f"\n📊 Analyzing {repo}...")

        try:
            analyzer = GitHubRepoAnalyzer(owner, name)
            result = analyzer.analyze()
            results[repo] = result
            print(f"   ✅ Success")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[repo] = {'error': str(e)}

    return results


def summarize_stacks(results: dict):
    """Print a summary of detected tech stacks"""
    print("\n" + "="*80)
    print("TECH STACK SUMMARY")
    print("="*80 + "\n")

    for repo, analysis in results.items():
        if 'error' in analysis:
            print(f"❌ {repo}: {analysis['error']}")
            continue

        frameworks = analysis['config_analysis']['frameworks']
        build_tools = analysis['config_analysis']['build_tools']
        primary_lang = analysis.get('primary_language', 'Unknown')

        print(f"📦 {repo}")
        print(f"   Primary: {primary_lang}")
        print(f"   Frameworks: {', '.join(frameworks) if frameworks else 'None detected'}")
        print(f"   Build Tools: {', '.join(build_tools) if build_tools else 'None detected'}")
        print()


def export_for_component_mapping(results: dict):
    """
    Export results in format useful for component library mapping

    This shows how you'd use this data to automatically select which
    UI component library to use for each project
    """
    mapping = {}

    for repo, analysis in results.items():
        if 'error' in analysis:
            continue

        frameworks = analysis['config_analysis']['frameworks']

        # Determine which component library to use
        component_lib = "Web Components (fallback)"  # Default

        if any(f in frameworks for f in ['React']):
            component_lib = "React Component Library"
        elif any(f in frameworks for f in ['Vue']):
            component_lib = "Vue Component Library"
        elif any(f in frameworks for f in ['Angular']):
            component_lib = "Angular Component Library"
        elif any(f in frameworks for f in ['Svelte']):
            component_lib = "Svelte Component Library"

        mapping[repo] = {
            'detected_frameworks': frameworks,
            'recommended_component_library': component_lib,
            'files_analyzed': len(analysis['file_analysis']['language_distribution']),
            'config_files_found': analysis['config_analysis']['config_files']
        }

    return mapping


if __name__ == "__main__":
    # Example: Analyze popular open source projects
    # (You'd use your own organization's repos)
    repos_to_analyze = [
        "facebook/react",           # React framework
        "vuejs/vue",               # Vue.js framework
        "angular/angular",         # Angular framework
        "psf/requests",            # Python library
        "torvalds/linux",          # C project
    ]

    print("\n" + "="*80)
    print("GITHUB REPO ANALYZER - BATCH ANALYSIS EXAMPLE")
    print("="*80)
    print(f"\nAnalyzing {len(repos_to_analyze)} repositories...")

    # Run analysis
    results = analyze_repos(repos_to_analyze)

    # Print summary
    summarize_stacks(results)

    # Generate component mapping
    mapping = export_for_component_mapping(results)

    print("\n" + "="*80)
    print("COMPONENT LIBRARY MAPPING (for your UI system)")
    print("="*80 + "\n")

    for repo, config in mapping.items():
        print(f"📦 {repo}")
        print(f"   → Use: {config['recommended_component_library']}")
        print(f"   → Detected: {', '.join(config['detected_frameworks']) or 'None'}")
        print()

    # Save detailed results
    with open('batch_analysis_results.json', 'w') as f:
        # Make results JSON serializable
        serializable_results = {repo: {
            k: v for k, v in analysis.items() if k != 'url'
        } for repo, analysis in results.items()}
        json.dump(serializable_results, f, indent=2)

    print("\n✅ Detailed results saved to: batch_analysis_results.json")
    print("\nYou can now use this data to:")
    print("  1. Assign UI component library to each project")
    print("  2. Validate component imports in PRs")
    print("  3. Generate component code in the right framework")
    print("  4. Enforce consistency across your organization")
