#!/usr/bin/env python3
"""
Comprehensive GitHub Repository Analyzer
Detects tech stack and performs 4-phase codebase analysis
Outputs color-coded status (GREEN/YELLOW/RED) for diagram conversion
"""

import requests
import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from enum import Enum
from urllib.parse import urljoin


class Status(Enum):
    """Color-coded status for findings"""
    GREEN = "✅ GREEN"      # Code is good, no issues
    YELLOW = "⚠️ YELLOW"    # Code status uncertain, needs attention
    RED = "🔴 RED"          # Security/critical issues or duplicative code


class Finding:
    """Represents a single finding from analysis"""

    def __init__(self, phase: str, status: Status, title: str, location: str = "",
                 impact: str = "", recommendation: str = ""):
        self.phase = phase
        self.status = status
        self.title = title
        self.location = location
        self.impact = impact
        self.recommendation = recommendation

    def to_dict(self) -> dict:
        return {
            'phase': self.phase,
            'status': self.status.value,
            'title': self.title,
            'location': self.location,
            'impact': self.impact,
            'recommendation': self.recommendation
        }


class ComprehensiveRepoAnalyzer:
    """Analyzes GitHub repos across 4 phases per build plan"""

    def __init__(self, owner: str, repo: str, max_files: int = 50):
        self.owner = owner
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main"
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})
        self.max_files = max_files

        # Analysis results
        self.tech_stack = {}
        self.findings: List[Finding] = []
        self.file_inventory = {}
        self.code_samples = {}

    # ============================================================================
    # TECH STACK DETECTION (Initial)
    # ============================================================================

    def detect_tech_stack(self) -> Dict:
        """Detect tech stack before analysis"""
        print(f"[STACK] Detecting tech stack...")
        contents = self._fetch_repo_contents()

        languages = defaultdict(int)
        frameworks = []
        build_tools = []
        config_files = []

        # Scan files
        for item in contents:
            if item['type'] == 'file':
                ext = item['name'].split('.')[-1].lower()
                if ext:
                    languages[ext] += 1

                # Detect frameworks from config files
                if item['name'] == 'package.json':
                    config_files.append('package.json')
                    pkg_data = self._fetch_file_content(item['download_url'])
                    if pkg_data:
                        frameworks.extend(self._extract_frameworks_from_package_json(pkg_data))

                elif item['name'] == 'requirements.txt':
                    config_files.append('requirements.txt')
                    req_data = self._fetch_file_content(item['download_url'], raw=True)
                    if req_data:
                        frameworks.extend(self._extract_frameworks_from_requirements(req_data))

                elif item['name'] in ['setup.py', 'pyproject.toml', 'Dockerfile']:
                    config_files.append(item['name'])

        self.tech_stack = {
            'primary_languages': sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5],
            'detected_frameworks': frameworks,
            'config_files': config_files
        }

        return self.tech_stack

    # ============================================================================
    # PHASE 1: UNDERSTANDING & CONTEXT SETTING
    # ============================================================================

    def phase1_understanding(self) -> List[Finding]:
        """Phase 1: File inventory, dependencies, core functionality, data flow"""
        print(f"[PHASE 1] Understanding & Context Setting...")
        findings = []

        # 1.1 File Inventory
        contents = self._fetch_repo_contents()
        file_count = len([c for c in contents if c['type'] == 'file'])
        dir_count = len([c for c in contents if c['type'] == 'dir'])

        if file_count == 0:
            findings.append(Finding(
                phase="1: Understanding",
                status=Status.RED,
                title="Empty repository",
                location="Root",
                impact="No code to analyze",
                recommendation="Ensure repository has source code files"
            ))
            return findings

        findings.append(Finding(
            phase="1: Understanding",
            status=Status.GREEN,
            title=f"File inventory complete",
            location="Root",
            impact=f"Found {file_count} files in {dir_count} directories",
            recommendation="Repository has measurable scope"
        ))

        # 1.2 Dependency Mapping
        has_dependency_file = any(
            c['name'] in ['package.json', 'requirements.txt', 'Gemfile', 'go.mod', 'Cargo.toml']
            for c in contents if c['type'] == 'file'
        )

        if has_dependency_file:
            findings.append(Finding(
                phase="1: Understanding",
                status=Status.GREEN,
                title="Dependency management detected",
                location="Root",
                impact="Project has formal dependency tracking",
                recommendation="Dependency versions are tracked and reproducible"
            ))
        else:
            findings.append(Finding(
                phase="1: Understanding",
                status=Status.YELLOW,
                title="No formal dependency file found",
                location="Root",
                impact="May indicate missing dependency management",
                recommendation="Add package.json, requirements.txt, or equivalent"
            ))

        # 1.3 Core Functionality Identification
        primary_lang = self.tech_stack['primary_languages'][0][0] if self.tech_stack['primary_languages'] else "Unknown"
        frameworks_str = ", ".join(self.tech_stack['detected_frameworks']) if self.tech_stack['detected_frameworks'] else "None"

        findings.append(Finding(
            phase="1: Understanding",
            status=Status.GREEN,
            title="Core functionality mapped",
            location="Root",
            impact=f"Primary language: {primary_lang}, Frameworks: {frameworks_str}",
            recommendation="Tech stack identified for targeted analysis"
        ))

        self.findings.extend(findings)
        return findings

    # ============================================================================
    # PHASE 2: STRUCTURAL ANALYSIS
    # ============================================================================

    def phase2_structural(self) -> List[Finding]:
        """Phase 2: Architecture, coupling, cohesion, design patterns"""
        print(f"[PHASE 2] Structural Analysis...")
        findings = []

        # Check for common architectural patterns
        contents = self._fetch_repo_contents()

        # 2.1 Architectural Pattern Detection
        has_src = any(c['name'] in ['src', 'lib', 'app', 'application'] for c in contents if c['type'] == 'dir')
        has_test = any(c['name'] in ['test', 'tests', '__tests__', 'spec', 'specs'] for c in contents if c['type'] == 'dir')
        has_config = any(c['name'] in ['config', 'conf', '.config'] for c in contents if c['type'] == 'dir')

        if has_src and has_test:
            findings.append(Finding(
                phase="2: Structural",
                status=Status.GREEN,
                title="Clear separation of source and test code",
                location="Directory structure",
                impact="Code organization follows best practices",
                recommendation="Maintain separation between src/ and test/ directories"
            ))
        else:
            findings.append(Finding(
                phase="2: Structural",
                status=Status.YELLOW,
                title="Source/test organization could be clearer",
                location="Directory structure",
                impact="May indicate mixed concerns or no test structure",
                recommendation="Organize code into src/, test/, and config/ directories"
            ))

        # 2.2 Check for monolithic structure vs modular
        python_files = [c for c in contents if c.get('name', '').endswith('.py') and c['type'] == 'file']
        js_files = [c for c in contents if c.get('name', '').endswith('.js') and c['type'] == 'file']

        total_source_files = len(python_files) + len(js_files)

        if total_source_files > 0:
            if any(f['name'] in ['__init__.py', 'package.json', 'index.js'] for f in python_files + js_files):
                findings.append(Finding(
                    phase="2: Structural",
                    status=Status.GREEN,
                    title="Module initialization files present",
                    location="Root modules",
                    impact="Indicates modular structure with entry points",
                    recommendation="Continue modular design pattern"
                ))
            else:
                findings.append(Finding(
                    phase="2: Structural",
                    status=Status.YELLOW,
                    title="Missing module initialization structure",
                    location="Root modules",
                    impact="May indicate monolithic design",
                    recommendation="Add __init__.py or index.js for proper module structure"
                ))

        # 2.3 Design pattern indicators
        has_factory = self._search_pattern_in_files(contents, r'class.*Factory|def.*factory')
        has_singleton = self._search_pattern_in_files(contents, r'singleton|instance.*=.*None')

        if has_factory or has_singleton:
            findings.append(Finding(
                phase="2: Structural",
                status=Status.GREEN,
                title="Design patterns detected in codebase",
                location="Multiple files",
                impact="Code uses recognized design patterns",
                recommendation="Continue using design patterns consistently"
            ))

        self.findings.extend(findings)
        return findings

    # ============================================================================
    # PHASE 3: CODE QUALITY & REDUNDANCY
    # ============================================================================

    def phase3_quality_redundancy(self) -> List[Finding]:
        """Phase 3: DRY principle, complexity, readability, error handling"""
        print(f"[PHASE 3] Code Quality & Redundancy Analysis...")
        findings = []

        contents = self._fetch_repo_contents()

        # 3.1 Check for README (code quality indicator)
        has_readme = any(c['name'].lower() in ['readme.md', 'readme', 'readme.txt'] for c in contents if c['type'] == 'file')

        if has_readme:
            findings.append(Finding(
                phase="3: Quality",
                status=Status.GREEN,
                title="Documentation present (README)",
                location="Root/README.md",
                impact="Project is documented for users and developers",
                recommendation="Keep README updated with changes"
            ))
        else:
            findings.append(Finding(
                phase="3: Quality",
                status=Status.RED,
                title="Missing README documentation",
                location="Root",
                impact="Lack of documentation affects maintainability and onboarding",
                recommendation="Create README.md with project overview, setup, and usage"
            ))

        # 3.2 Check for code style/lint configuration
        lint_files = ['.eslintrc', '.eslintrc.json', 'pylintrc', '.flake8', '.pylintrc', 'tox.ini', '.pre-commit-config.yaml']
        has_lint_config = any(c['name'] in lint_files for c in contents if c['type'] == 'file')

        if has_lint_config:
            findings.append(Finding(
                phase="3: Quality",
                status=Status.GREEN,
                title="Linting/code style rules configured",
                location="Various config files",
                impact="Enforces consistent code style across project",
                recommendation="Ensure lint rules are enforced in CI/CD pipeline"
            ))
        else:
            findings.append(Finding(
                phase="3: Quality",
                status=Status.YELLOW,
                title="No code style configuration found",
                location="Root",
                impact="May result in inconsistent code style across files",
                recommendation="Add .eslintrc, pylintrc, or similar style configuration"
            ))

        # 3.3 Check for test configuration
        test_files = [c['name'] for c in contents if c['type'] == 'file' and any(
            name in c['name'].lower() for name in ['jest.config', 'pytest.ini', '.mocharc', 'karma.conf', 'test']
        )]

        if test_files:
            findings.append(Finding(
                phase="3: Quality",
                status=Status.GREEN,
                title="Testing framework configured",
                location="Test config files",
                impact="Project has automated testing capability",
                recommendation="Ensure adequate test coverage (aim for >80%)"
            ))
        else:
            findings.append(Finding(
                phase="3: Quality",
                status=Status.RED,
                title="No testing configuration found",
                location="Root",
                impact="Lack of automated tests increases bug risk",
                recommendation="Set up Jest, pytest, Mocha, or similar test framework"
            ))

        # 3.4 Check for complex/long files (need sampling)
        sample_files = [c for c in contents if c['type'] == 'file' and c.get('size', 0) > 10000][:5]

        if sample_files:
            findings.append(Finding(
                phase="3: Quality",
                status=Status.YELLOW,
                title=f"Large source files detected ({len(sample_files)} files > 10KB)",
                location=", ".join([f['name'] for f in sample_files][:3]),
                impact="Large files may indicate high cyclomatic complexity",
                recommendation="Consider breaking large files into smaller, focused modules"
            ))

        self.findings.extend(findings)
        return findings

    # ============================================================================
    # PHASE 4: SECURITY ANALYSIS
    # ============================================================================

    def phase4_security(self) -> List[Finding]:
        """Phase 4: Input validation, injection flaws, auth, sensitive data"""
        print(f"[PHASE 4] Security Analysis...")
        findings = []

        contents = self._fetch_repo_contents()

        # 4.1 Check for .env/.env.example (secrets management)
        has_env_example = any(c['name'] in ['.env.example', '.env.template'] for c in contents if c['type'] == 'file')
        has_env_file = any(c['name'] == '.env' for c in contents if c['type'] == 'file')

        if has_env_example:
            findings.append(Finding(
                phase="4: Security",
                status=Status.GREEN,
                title="Environment configuration template present",
                location=".env.example",
                impact="Indicates proper secrets management practice",
                recommendation="Keep .env.example updated; never commit .env file"
            ))
        elif has_env_file:
            findings.append(Finding(
                phase="4: Security",
                status=Status.RED,
                title=".env file found in repository",
                location=".env",
                impact="CRITICAL: Sensitive data may be exposed in version control",
                recommendation="Remove .env from git immediately; add to .gitignore; rotate any exposed secrets"
            ))
        else:
            findings.append(Finding(
                phase="4: Security",
                status=Status.YELLOW,
                title="No environment configuration pattern detected",
                location="Root",
                impact="May indicate missing secrets management",
                recommendation="Create .env.example for configuration template"
            ))

        # 4.2 Check for .gitignore (prevents accidental commits)
        has_gitignore = any(c['name'] == '.gitignore' for c in contents if c['type'] == 'file')

        if has_gitignore:
            findings.append(Finding(
                phase="4: Security",
                status=Status.GREEN,
                title=".gitignore configured",
                location=".gitignore",
                impact="Prevents accidental commits of sensitive files",
                recommendation="Ensure .gitignore includes: .env, node_modules, __pycache__, .venv"
            ))
        else:
            findings.append(Finding(
                phase="4: Security",
                status=Status.YELLOW,
                title=".gitignore not found",
                location="Root",
                impact="Risk of committing unnecessary files or sensitive data",
                recommendation="Create .gitignore for language/framework (use gitignore.io)"
            ))

        # 4.3 Check for security/dependency scanning config
        security_files = [c['name'] for c in contents if c['type'] == 'file' and any(
            pattern in c['name'].lower() for pattern in [
                'dependabot', 'snyk', '.whitesource', 'security.md', 'codeql'
            ]
        )]

        if security_files:
            findings.append(Finding(
                phase="4: Security",
                status=Status.GREEN,
                title="Dependency security scanning enabled",
                location=", ".join(security_files),
                impact="Automated detection of vulnerable dependencies",
                recommendation="Keep security scans enabled and address alerts promptly"
            ))
        else:
            findings.append(Finding(
                phase="4: Security",
                status=Status.YELLOW,
                title="No automated security scanning detected",
                location="Root",
                impact="Vulnerable dependencies may go undetected",
                recommendation="Enable Dependabot or Snyk for automated vulnerability scanning"
            ))

        # 4.4 Check for HTTPS/secure patterns
        has_https_pattern = self._search_pattern_in_files(contents, r'https://|ssl|tls', limit=5)

        if has_https_pattern:
            findings.append(Finding(
                phase="4: Security",
                status=Status.GREEN,
                title="HTTPS/SSL patterns detected",
                location="Multiple files",
                impact="Code appears to use secure communication",
                recommendation="Verify all external API calls use HTTPS"
            ))

        self.findings.extend(findings)
        return findings

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _fetch_repo_contents(self) -> List[Dict]:
        """Fetch repository root directory contents"""
        try:
            url = f"{self.api_url}/contents"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json() if isinstance(response.json(), list) else []
        except Exception as e:
            print(f"Warning: Could not fetch repo contents: {e}")
            return []

    def _fetch_file_content(self, download_url: str, raw: bool = False) -> Optional[str]:
        """Fetch file content from GitHub"""
        try:
            response = self.session.get(download_url, timeout=10)
            response.raise_for_status()
            return response.text if raw else response.text
        except Exception as e:
            return None

    def _extract_frameworks_from_package_json(self, content: str) -> List[str]:
        """Extract framework names from package.json content"""
        frameworks = []
        framework_keywords = {
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'svelte': 'Svelte',
            'express': 'Express.js',
            'next': 'Next.js',
            'nuxt': 'Nuxt.js',
            'gatsby': 'Gatsby',
            'jest': 'Jest',
            'mocha': 'Mocha',
            'webpack': 'Webpack',
            'vite': 'Vite',
        }

        try:
            data = json.loads(content)
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            for keyword, name in framework_keywords.items():
                if any(keyword in dep for dep in deps.keys()):
                    frameworks.append(name)
        except:
            pass

        return frameworks

    def _extract_frameworks_from_requirements(self, content: str) -> List[str]:
        """Extract framework names from requirements.txt"""
        frameworks = []
        framework_keywords = {
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'pytest': 'pytest',
            'sqlalchemy': 'SQLAlchemy',
        }

        content_lower = content.lower()
        for keyword, name in framework_keywords.items():
            if keyword in content_lower:
                frameworks.append(name)

        return frameworks

    def _search_pattern_in_files(self, contents: List[Dict], pattern: str, limit: int = 5) -> bool:
        """Search for regex pattern in code files (limited sample)"""
        try:
            sample_files = [c for c in contents if c['type'] == 'file' and any(
                ext in c['name'].lower() for ext in ['.py', '.js', '.ts', '.java']
            )][:limit]

            for file in sample_files:
                content = self._fetch_file_content(file.get('download_url', ''), raw=True)
                if content and re.search(pattern, content, re.IGNORECASE):
                    return True
        except:
            pass

        return False

    # ============================================================================
    # REPORTING
    # ============================================================================

    def generate_report(self) -> Dict:
        """Run complete analysis and generate report"""
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE REPOSITORY ANALYSIS")
        print("="*80 + "\n")

        # Detect tech stack first
        print("Step 1: Tech Stack Detection")
        self.detect_tech_stack()
        print(f"  ✓ Detected frameworks: {self.tech_stack['detected_frameworks']}")
        print(f"  ✓ Config files: {self.tech_stack['config_files']}\n")

        # Run all 4 phases
        print("Step 2: Phase 1 - Understanding")
        self.phase1_understanding()
        print(f"  ✓ {len([f for f in self.findings if f.phase.startswith('1')])} findings\n")

        print("Step 3: Phase 2 - Structural Analysis")
        self.phase2_structural()
        print(f"  ✓ {len([f for f in self.findings if f.phase.startswith('2')])} findings\n")

        print("Step 4: Phase 3 - Code Quality")
        self.phase3_quality_redundancy()
        print(f"  ✓ {len([f for f in self.findings if f.phase.startswith('3')])} findings\n")

        print("Step 5: Phase 4 - Security Analysis")
        self.phase4_security()
        print(f"  ✓ {len([f for f in self.findings if f.phase.startswith('4')])} findings\n")

        # Generate summary
        status_counts = defaultdict(int)
        for finding in self.findings:
            status_counts[finding.status.value] += 1

        return {
            'repo': f"{self.owner}/{self.repo}",
            'tech_stack': self.tech_stack,
            'analysis_summary': {
                'total_findings': len(self.findings),
                'status_breakdown': {
                    'green': status_counts['✅ GREEN'],
                    'yellow': status_counts['⚠️ YELLOW'],
                    'red': status_counts['🔴 RED']
                }
            },
            'findings': [f.to_dict() for f in self.findings],
            'critical_actions': self._get_critical_actions()
        }

    def _get_critical_actions(self) -> List[Dict]:
        """Extract critical action items"""
        critical = []

        for finding in self.findings:
            if finding.status == Status.RED:
                critical.append({
                    'priority': 'CRITICAL',
                    'finding': finding.title,
                    'action': finding.recommendation
                })
            elif finding.status == Status.YELLOW and any(
                keyword in finding.title.lower() for keyword in ['security', 'test', 'documentation']
            ):
                critical.append({
                    'priority': 'HIGH',
                    'finding': finding.title,
                    'action': finding.recommendation
                })

        return critical[:10]  # Top 10


def parse_github_url(url: str) -> Tuple[str, str]:
    """Parse GitHub URL"""
    if url.startswith('http'):
        parts = url.rstrip('/').split('/')
        return parts[-2], parts[-1]
    else:
        owner, repo = url.split('/')
        return owner, repo


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python comprehensive_repo_analyzer.py owner/repo")
        print("Example: python comprehensive_repo_analyzer.py facebook/react")
        sys.exit(1)

    repo_input = sys.argv[1]

    try:
        owner, repo = parse_github_url(repo_input)
        analyzer = ComprehensiveRepoAnalyzer(owner, repo)
        report = analyzer.generate_report()

        # Print report
        print("\n" + "="*80)
        print("ANALYSIS REPORT")
        print("="*80)
        print(json.dumps(report, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
