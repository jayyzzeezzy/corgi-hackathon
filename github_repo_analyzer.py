#!/usr/bin/env python3
"""
GitHub Repository Tech Stack Analyzer
Analyzes public GitHub repos to detect languages, frameworks, and technologies
"""

import requests
import json
from collections import defaultdict
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class GitHubRepoAnalyzer:
    """Analyzes GitHub repos without authentication (public repos only)"""

    # File extensions mapped to languages
    LANGUAGE_EXTENSIONS = {
        'py': 'Python',
        'js': 'JavaScript',
        'jsx': 'JavaScript/React',
        'ts': 'TypeScript',
        'tsx': 'TypeScript/React',
        'java': 'Java',
        'class': 'Java',
        'cpp': 'C++',
        'c': 'C',
        'cs': 'C#',
        'rb': 'Ruby',
        'go': 'Go',
        'rs': 'Rust',
        'php': 'PHP',
        'swift': 'Swift',
        'kt': 'Kotlin',
        'scala': 'Scala',
        'r': 'R',
        'lua': 'Lua',
        'sh': 'Shell/Bash',
        'bash': 'Shell/Bash',
        'sql': 'SQL',
        'html': 'HTML',
        'css': 'CSS',
        'scss': 'SCSS',
        'sass': 'SASS',
        'less': 'LESS',
        'vue': 'Vue.js',
        'svelte': 'Svelte',
    }

    # Config files that indicate specific tech
    CONFIG_INDICATORS = {
        'package.json': ('Node.js/JavaScript', {'framework': 'check_package_json'}),
        'requirements.txt': ('Python', {'framework': 'check_requirements'}),
        'setup.py': ('Python', {'framework': 'check_setup_py'}),
        'Pipfile': ('Python', {'framework': 'check_pipfile'}),
        'pyproject.toml': ('Python', {'framework': 'check_pyproject'}),
        'Dockerfile': ('Docker', {}),
        'docker-compose.yml': ('Docker Compose', {}),
        'Gemfile': ('Ruby', {'framework': 'check_gemfile'}),
        'go.mod': ('Go', {}),
        'Cargo.toml': ('Rust', {}),
        'pom.xml': ('Java/Maven', {}),
        'build.gradle': ('Java/Gradle', {}),
        'gradle.properties': ('Java/Gradle', {}),
        '.nvmrc': ('Node.js', {}),
        '.node-version': ('Node.js', {}),
        'tsconfig.json': ('TypeScript', {}),
        'webpack.config.js': ('Webpack', {}),
        'vite.config.js': ('Vite', {}),
        'vite.config.ts': ('Vite', {}),
        'next.config.js': ('Next.js', {}),
        'nuxt.config.js': ('Nuxt.js', {}),
        'gatsby-config.js': ('Gatsby', {}),
        '.prettierrc': ('JavaScript/Prettier', {}),
        '.eslintrc': ('JavaScript/ESLint', {}),
        'tox.ini': ('Python/Tox', {}),
        'pytest.ini': ('Python/pytest', {}),
        'Makefile': ('Build Automation', {}),
        'CMakeLists.txt': ('C/C++/CMake', {}),
    }

    def __init__(self, owner: str, repo: str):
        """
        Initialize analyzer for a GitHub repo

        Args:
            owner: GitHub username/org
            repo: Repository name
        """
        self.owner = owner
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main"
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/vnd.github.v3+json'})

    def fetch_repo_info(self) -> Dict:
        """Fetch basic repo info"""
        try:
            response = self.session.get(self.api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch repo info: {e}")

    def fetch_repo_contents(self, path: str = "") -> List[Dict]:
        """Fetch directory contents from repo"""
        try:
            url = f"{self.api_url}/contents/{path}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            if isinstance(response.json(), list):
                return response.json()
            return [response.json()] if response.json() else []
        except requests.RequestException as e:
            print(f"Warning: Could not fetch {path}: {e}")
            return []

    def analyze_languages(self) -> Dict[str, int]:
        """Scan repo and count file types by language"""
        languages = defaultdict(int)

        # Get root directory contents
        contents = self.fetch_repo_contents()

        def scan_directory(items: List[Dict], depth: int = 0):
            """Recursively scan directories (limited depth)"""
            if depth > 2:  # Limit recursion to avoid excessive API calls
                return

            for item in items:
                if item['type'] == 'file':
                    ext = item['name'].split('.')[-1].lower() if '.' in item['name'] else ''
                    if ext in self.LANGUAGE_EXTENSIONS:
                        languages[self.LANGUAGE_EXTENSIONS[ext]] += 1
                    else:
                        # Count unknown files too
                        languages[f'Other ({ext})'] += 1

                elif item['type'] == 'dir' and depth < 2:
                    # Skip common unimportant directories
                    skip_dirs = {'.git', 'node_modules', '.venv', 'venv', '.env',
                               '__pycache__', '.pytest_cache', 'dist', 'build'}
                    if item['name'] not in skip_dirs:
                        sub_contents = self.fetch_repo_contents(item['path'])
                        scan_directory(sub_contents, depth + 1)

        scan_directory(contents)
        return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))

    def analyze_config_files(self) -> Dict[str, any]:
        """Check for config files that indicate tech stack"""
        detected = {
            'frameworks': [],
            'build_tools': [],
            'config_files_found': []
        }

        contents = self.fetch_repo_contents()
        file_names = {item['name'] for item in contents if item['type'] == 'file'}

        for config_file, (tech, checkers) in self.CONFIG_INDICATORS.items():
            if config_file in file_names:
                detected['config_files_found'].append(config_file)
                if 'framework' not in tech.lower():
                    detected['build_tools'].append(tech)
                else:
                    detected['frameworks'].append(tech)

                # Run specific checkers if available
                for checker_name in checkers.get('framework', []):
                    if hasattr(self, checker_name):
                        result = getattr(self, checker_name)(contents)
                        if result:
                            detected['frameworks'].extend(result)

        return detected

    def check_package_json(self, contents: List[Dict]) -> List[str]:
        """Analyze package.json for frameworks"""
        frameworks = []

        pkg_file = next((c for c in contents if c['name'] == 'package.json'), None)
        if not pkg_file:
            return frameworks

        try:
            response = self.session.get(pkg_file['download_url'], timeout=10)
            pkg_data = response.json()

            deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}

            # Check for common frameworks
            framework_checks = {
                'react': 'React',
                'vue': 'Vue.js',
                'svelte': 'Svelte',
                'angular': 'Angular',
                'express': 'Express.js',
                'fastify': 'Fastify',
                'nestjs': 'NestJS',
                'next': 'Next.js',
                'nuxt': 'Nuxt.js',
                'gatsby': 'Gatsby',
                'remix': 'Remix',
                'astro': 'Astro',
                'solid': 'SolidJS',
                'preact': 'Preact',
                'graphql': 'GraphQL',
                'apollo': 'Apollo',
                'webpack': 'Webpack',
                'vite': 'Vite',
                'rollup': 'Rollup',
                'parcel': 'Parcel',
                'jest': 'Jest',
                'vitest': 'Vitest',
                'mocha': 'Mocha',
            }

            for dep_name, framework in framework_checks.items():
                if any(dep_name in dep for dep in deps.keys()):
                    frameworks.append(framework)

        except Exception as e:
            print(f"Warning: Could not analyze package.json: {e}")

        return frameworks

    def check_requirements(self, contents: List[Dict]) -> List[str]:
        """Analyze requirements.txt"""
        frameworks = []
        req_file = next((c for c in contents if c['name'] == 'requirements.txt'), None)
        if req_file:
            try:
                response = self.session.get(req_file['download_url'], timeout=10)
                content = response.text.lower()

                framework_checks = {
                    'django': 'Django',
                    'flask': 'Flask',
                    'fastapi': 'FastAPI',
                    'starlette': 'Starlette',
                    'tornado': 'Tornado',
                    'aiohttp': 'aiohttp',
                    'pytest': 'pytest',
                    'unittest': 'unittest',
                    'sqlalchemy': 'SQLAlchemy',
                    'pandas': 'Pandas',
                    'numpy': 'NumPy',
                    'scipy': 'SciPy',
                    'tensorflow': 'TensorFlow',
                    'torch': 'PyTorch',
                    'scikit': 'Scikit-learn',
                }

                for dep_name, framework in framework_checks.items():
                    if dep_name in content:
                        frameworks.append(framework)
            except Exception as e:
                print(f"Warning: Could not analyze requirements.txt: {e}")

        return frameworks

    def analyze(self) -> Dict:
        """Run complete analysis"""
        print(f"Analyzing {self.owner}/{self.repo}...")

        try:
            repo_info = self.fetch_repo_info()
            languages = self.analyze_languages()
            config_info = self.analyze_config_files()

            analysis = {
                'repo': f"{self.owner}/{self.repo}",
                'url': repo_info.get('html_url'),
                'description': repo_info.get('description'),
                'primary_language': repo_info.get('language'),
                'file_analysis': {
                    'language_distribution': languages,
                },
                'config_analysis': {
                    'frameworks': list(set(config_info['frameworks'])),
                    'build_tools': list(set(config_info['build_tools'])),
                    'config_files': config_info['config_files_found'],
                },
                'summary': self._generate_summary(repo_info, languages, config_info)
            }

            return analysis

        except Exception as e:
            return {
                'error': str(e),
                'repo': f"{self.owner}/{self.repo}"
            }

    def _generate_summary(self, repo_info: Dict, languages: Dict, config: Dict) -> str:
        """Generate human-readable summary"""
        parts = []

        # Primary language
        primary = repo_info.get('language')
        if primary:
            parts.append(f"**Primary Language**: {primary}")

        # Top languages detected
        if languages:
            top_langs = ', '.join([f"{lang} ({count})" for lang, count in list(languages.items())[:3]])
            parts.append(f"**Top Languages**: {top_langs}")

        # Frameworks
        if config['frameworks']:
            parts.append(f"**Frameworks**: {', '.join(set(config['frameworks']))}")

        # Build tools
        if config['build_tools']:
            parts.append(f"**Build/Tools**: {', '.join(set(config['build_tools']))}")

        return ' | '.join(parts)


def parse_github_url(url: str) -> Tuple[str, str]:
    """Parse GitHub URL to owner and repo"""
    # Handle: https://github.com/owner/repo or owner/repo
    if url.startswith('http'):
        parts = url.rstrip('/').split('/')
        return parts[-2], parts[-1]
    else:
        owner, repo = url.split('/')
        return owner, repo


# Example usage
if __name__ == "__main__":
    import sys

    # Accept repo from command line or use example
    if len(sys.argv) > 1:
        repo_input = sys.argv[1]
    else:
        # Example: analyze the Python requests library
        repo_input = "psf/requests"

    try:
        owner, repo = parse_github_url(repo_input)
        analyzer = GitHubRepoAnalyzer(owner, repo)
        result = analyzer.analyze()

        # Pretty print results
        print("\n" + "="*70)
        print(f"TECH STACK ANALYSIS: {result['repo']}")
        print("="*70)
        print(json.dumps(result, indent=2))
        print("\n" + "="*70)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
