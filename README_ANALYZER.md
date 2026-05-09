# GitHub Repository Tech Stack Analyzer

Analyzes **public GitHub repositories** without authentication to detect:
- Programming languages and file distribution
- Frameworks and libraries in use
- Build tools and build systems
- Configuration files indicating tech stack

## Why This Matters for Your UI Component System

This is **Step 1** of your UI component standardization project. Before you can enforce component consistency across projects, you need to:

1. **Identify what stack each project uses** (this tool)
2. **Recommend appropriate components** for that stack
3. **Validate component usage** as code is written
4. **Generate unified component libraries** for each framework

This analyzer gives you the foundation to do all of that.

## Installation

```bash
# No external dependencies needed beyond Python 3.7+
# Only uses standard library + requests (pip install requests)

pip install requests
```

## Usage

### Command Line

```bash
# Analyze a public GitHub repo
python analyze_repo.py owner/repo
python analyze_repo.py https://github.com/owner/repo

# Export results to JSON
python analyze_repo.py facebook/react --export
python analyze_repo.py psf/requests -e
```

### In Python Code

```python
from github_repo_analyzer import GitHubRepoAnalyzer

# Create analyzer
analyzer = GitHubRepoAnalyzer("facebook", "react")

# Run analysis
result = analyzer.analyze()

# Result structure:
# {
#   'repo': 'facebook/react',
#   'url': 'https://github.com/facebook/react',
#   'primary_language': 'JavaScript',
#   'file_analysis': {
#     'language_distribution': {
#       'JavaScript': 450,
#       'TypeScript': 200,
#       ...
#     }
#   },
#   'config_analysis': {
#     'frameworks': ['React', 'Jest'],
#     'build_tools': ['Webpack', 'Babel'],
#     'config_files': ['package.json', 'webpack.config.js', ...]
#   },
#   'summary': '...'
# }
```

## What It Detects

### Languages (by file extension)
- Python, JavaScript, TypeScript, Java, C++, C, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, R, Lua, Shell/Bash, SQL, HTML, CSS, Vue, Svelte

### Frameworks (from package.json)
- **JavaScript/Node.js**: React, Vue, Angular, Svelte, Next.js, Nuxt.js, Gatsby, Express, NestJS, Fastify
- **Python**: Django, Flask, FastAPI, Starlette, Tornado
- **Build Tools**: Webpack, Vite, Rollup, Parcel, Gulp, Grunt

### Config Files Detected
- `package.json`, `requirements.txt`, `setup.py`, `pyproject.toml`, `Pipfile`
- `tsconfig.json`, `webpack.config.js`, `vite.config.js`
- `next.config.js`, `nuxt.config.js`, `gatsby-config.js`
- `Dockerfile`, `docker-compose.yml`, `Makefile`
- `.eslintrc`, `.prettierrc`, `pytest.ini`, `tox.ini`
- And 20+ others

## Example Output

```
================================================================================
📊 GITHUB REPOSITORY ANALYSIS
================================================================================

📦 Repository: facebook/react
   URL: https://github.com/facebook/react
   Description: A JavaScript library for building user interfaces...

🔍 FILE ANALYSIS
────────────────────────────────────────────────────────────────────────────────
   Language Distribution:
     JavaScript....................... 450 files (65.2%) ████████████
     TypeScript....................... 200 files (29.0%) ██████
     CSS............................. 35 files (5.1%) █
     Shell/Bash...................... 10 files (1.4%)
     Other (json).................... 8 files (1.2%)

⚙️  TECH STACK DETECTION
────────────────────────────────────────────────────────────────────────────────
   Frameworks: React, Jest, Webpack, Babel
   Build Tools: Webpack, Rollup, Vite
   Config Files Found: package.json, webpack.config.js, .eslintrc

📈 SUMMARY
────────────────────────────────────────────────────────────────────────────────
   Primary Language (GitHub): JavaScript | Top Languages: JavaScript (450) |
   Frameworks: React, Jest, Webpack | Build/Tools: Webpack, Rollup, Vite

================================================================================
```

## API Rate Limits

Since this uses **public GitHub API without authentication**:
- **Rate limit**: 60 requests/hour per IP address
- Sufficient for analyzing several repos
- If analyzing many repos, use optional authentication (add GitHub token) for 5,000/hour

### Adding Authentication (optional)

```python
import os
from github_repo_analyzer import GitHubRepoAnalyzer

os.environ['GITHUB_TOKEN'] = 'your_github_token'

analyzer = GitHubRepoAnalyzer("owner", "repo")
# Update session header to use token:
analyzer.session.headers['Authorization'] = f"token {os.environ['GITHUB_TOKEN']}"
```

## How to Use This in Your UI Component System

### Phase 1: Catalog Existing Projects (Current)
```python
# Scan your organization's repos
repos = [
    "yourorg/project-alpha",
    "yourorg/project-beta", 
    "yourorg/project-gamma"
]

from github_repo_analyzer import GitHubRepoAnalyzer

for repo in repos:
    owner, name = repo.split('/')
    analyzer = GitHubRepoAnalyzer(owner, name)
    result = analyzer.analyze()
    
    # Save to database or JSON
    print(f"{repo}: {result['config_analysis']['frameworks']}")
```

### Phase 2: Build Stack-Specific Component Libraries
Once you know each project's stack:
- React projects → Use React component library
- Vue projects → Use Vue component library  
- Svelte projects → Use Svelte component library
- Multi-framework → Use Web Components

### Phase 3: Validate Components in PRs
Extend this analyzer to:
- Parse the project's config to detect framework
- Read the PR's component imports
- Validate they match approved component library for that stack
- Comment on PR if violations found

### Phase 4: Auto-generate Components
Use the detected framework to:
- Fetch component specs from your component library
- Generate boilerplate code in the correct framework
- Output to project in proper directory

## Files Included

| File | Purpose |
|------|---------|
| `github_repo_analyzer.py` | Core analyzer class (no dependencies) |
| `analyze_repo.py` | CLI wrapper with pretty printing |
| `README_ANALYZER.md` | This file |

## Next Steps in Your Component Project

1. ✅ **Step 1 (Done)**: Analyze repos to detect tech stack → You are here
2. **Step 2**: Create UI component specification (skills file)
3. **Step 3**: Build component validator that checks PRs
4. **Step 4**: Create component generator for each framework
5. **Step 5**: Build 3 demo apps showing unified components across different stacks

---

**Ready to build the component library specs next?** Let me know what frameworks/UI component categories you want to standardize on.
