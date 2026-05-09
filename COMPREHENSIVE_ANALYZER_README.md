# Comprehensive Repository Analyzer

A sophisticated GitHub repository analysis tool that implements your 4-phase build plan with color-coded status reporting for easy diagram conversion.

## Overview

This system analyzes public GitHub repositories without authentication and provides:

1. **Tech Stack Detection** - Identifies frameworks, languages, and tools
2. **4-Phase Analysis** (following your build plan):
   - **Phase 1: Understanding** - File inventory, dependencies, core functionality
   - **Phase 2: Structural** - Architecture, coupling, design patterns
   - **Phase 3: Quality** - DRY, complexity, readability, testing
   - **Phase 4: Security** - Input validation, secrets, scanning, HTTPS

3. **Color-Coded Status** for easy visualization:
   - 🟢 **GREEN** - Code is good, no issues
   - 🟡 **YELLOW** - Code status uncertain, needs attention
   - 🔴 **RED** - Security/critical issues or duplicative code

4. **Multiple Output Formats** ready for diagram conversion:
   - Table (human-readable)
   - JSON (structured data)
   - CSV (spreadsheet analysis)
   - Mermaid (flowchart syntax)
   - D3.js JSON (visualization-ready)

## Files

| File | Purpose |
|------|---------|
| `comprehensive_repo_analyzer.py` | Core analyzer (4-phase analysis logic) |
| `comprehensive_analyzer_cli.py` | CLI with output formatters |
| `COMPREHENSIVE_ANALYZER_README.md` | This documentation |

## Installation

```bash
# Only requires Python 3.7+ and requests library
pip install requests
```

## Quick Start

```bash
# Analyze a repository
python comprehensive_analyzer_cli.py facebook/react

# Get structured output
python comprehensive_analyzer_cli.py facebook/react --format json

# Get diagram-ready Mermaid syntax
python comprehensive_analyzer_cli.py facebook/react --format mermaid

# Export to CSV for spreadsheet analysis
python comprehensive_analyzer_cli.py facebook/react --format csv

# Get D3.js visualization data
python comprehensive_analyzer_cli.py facebook/react --format d3json
```

## Output Formats Explained

### 1. Table Format (Default)
Human-readable summary with:
- Overview of status breakdown
- Table of all findings with phase, status, title, location
- Detailed findings with impact and recommendations
- Critical action items

**Use when:** You need to read and understand findings quickly

```
Repository: facebook/react
Total Findings: 12
  ✅ GREEN (Good): 7
  ⚠️ YELLOW (Needs attention): 3
  🔴 RED (Critical): 2

[Detailed table and recommendations follow]
```

### 2. JSON Format
Complete structured data with all findings, tech stack detection, and critical actions.

**Use when:** You need to programmatically process or import data

```bash
python comprehensive_analyzer_cli.py facebook/react --format json > react_analysis.json
```

### 3. Mermaid Format
Flowchart syntax showing analysis phases and status breakdown.

**Use when:** You want to create visual diagrams**Generates:**
```mermaid
graph TD
    Repo["📦 facebook/react"]
    Phase1["Phase 1: Understanding<br/>✅ 3 🟡 1 🔴 0"]
    ...
```

Can be rendered in:
- GitHub markdown (native support)
- Notion (built-in Mermaid support)
- Draw.io (with Mermaid plugin)
- Online Mermaid editor

### 4. CSV Format
Tabular data for spreadsheet analysis.

**Use when:** You want to analyze in Excel, Google Sheets, or Tableau

```csv
Phase,Status,Title,Location,Impact,Recommendation
1: Understanding,✅ GREEN,File inventory complete,Root,...
```

### 5. D3.js JSON Format
Node-link graph structure for interactive visualization.

**Use when:** You want to build interactive dashboards

```json
{
  "nodes": [
    {"id": "repo", "label": "facebook/react", "type": "repo"},
    {"id": "phase_1", "label": "Phase 1: Understanding", "type": "phase"},
    {"id": "finding_0", "label": "File inventory complete", "type": "finding", "status": "green"}
  ],
  "links": [
    {"source": "repo", "target": "phase_1"},
    {"source": "phase_1", "target": "finding_0"}
  ]
}
```

## Analysis Phases Explained

### Phase 1: Understanding & Context Setting

Answers: "What is this project?"

**Checks:**
- ✅ Repository has code files
- ✅ Formal dependency management (package.json, requirements.txt, etc.)
- ✅ Tech stack identification
- ✅ Core functionality mapped

### Phase 2: Structural Analysis

Answers: "Is the code well-organized?"

**Checks:**
- ✅ Separation of source and test code
- ✅ Modular vs. monolithic structure
- ✅ Design pattern usage (Factory, Singleton, etc.)
- ✅ Module initialization present

### Phase 3: Code Quality & Redundancy

Answers: "Is the code maintainable?"

**Checks:**
- ✅ README documentation exists
- ✅ Code style/linting configured
- ✅ Testing framework configured
- ✅ No overly large/complex files
- ✅ No code duplication patterns

### Phase 4: Security Analysis

Answers: "Is the code secure?"

**Checks:**
- ✅ Environment configuration (.env.example)
- ✅ No secrets exposed (.env not in repo)
- ✅ .gitignore configured properly
- ✅ Security scanning enabled (Dependabot, Snyk)
- ✅ HTTPS/SSL patterns present

## Color-Coded Status System

### 🟢 GREEN - Code is Good
```
✅ File inventory complete
✅ Documentation present (README)
✅ Testing framework configured
✅ Security scanning enabled
```

**Action:** Monitor and maintain. These are strengths.

### 🟡 YELLOW - Needs Attention
```
⚠️ Source/test organization could be clearer
⚠️ No code style configuration found
⚠️ No formal dependency file found
⚠️ Environment configuration pattern not detected
```

**Action:** Should be addressed in medium term (next sprint/release).

### 🔴 RED - Critical Issues
```
🔴 Missing README documentation
🔴 No testing configuration found
🔴 .env file found in repository (SECURITY RISK)
🔴 Hardcoded secrets detected
```

**Action:** Must be addressed immediately (blocking issues).

## Example: Complete Analysis Workflow

```bash
# 1. Analyze repository
python comprehensive_analyzer_cli.py facebook/react --format table

# 2. Get structured data
python comprehensive_analyzer_cli.py facebook/react --format json > react_analysis.json

# 3. Generate diagram syntax
python comprehensive_analyzer_cli.py facebook/react --format mermaid > react_diagram.md

# 4. Export for spreadsheet review
python comprehensive_analyzer_cli.py facebook/react --format csv > react_findings.csv

# 5. Prepare for visualization
python comprehensive_analyzer_cli.py facebook/react --format d3json > react_visualization.json
```

## Building Diagrams from Output

### Option 1: GitHub-Rendered Mermaid
1. Copy Mermaid output to `.md` file
2. Commit to GitHub
3. View rendered in GitHub (automatic)

### Option 2: Draw.io
1. Export as Mermaid format
2. Open draw.io
3. File → Import → Paste Mermaid code
4. Diagram renders automatically
5. Add colors/styling in UI

### Option 3: D3.js Dashboard
Use the D3JSON output with a custom visualization:

```html
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
  fetch('react_visualization.json')
    .then(r => r.json())
    .then(data => {
      // Create force simulation
      const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(width/2, height/2));
      
      // Color nodes by status
      // green: #90EE90, yellow: #FFD700, red: #FF6B6B
    });
</script>
```

### Option 4: Tableau/PowerBI
1. Export as CSV format
2. Import into Tableau/PowerBI
3. Create custom visualization with:
   - Color field: Status (maps to color)
   - Rows: Phase
   - Values: Count of findings
   - Filters: Status type

## Key Features for Your UI Component System

This analyzer is **Step 1.5** of your UI component standardization:

1. ✅ **Step 1**: Tech stack detection → identifies React/Vue/Svelte projects
2. **This tool**: Comprehensive repo analysis → validates code quality baseline
3. **Step 2**: Component specifications → define standard UI components
4. **Step 3**: Component validator → enforce usage in PRs
5. **Step 4**: Demo apps → prove consistency across frameworks

## Advanced Usage

### Batch Analysis Script

```python
from comprehensive_repo_analyzer import ComprehensiveRepoAnalyzer

repos = [
    'facebook/react',
    'vuejs/vue',
    'angular/angular'
]

for repo in repos:
    owner, name = repo.split('/')
    analyzer = ComprehensiveRepoAnalyzer(owner, name)
    report = analyzer.generate_report()
    
    # Process report (save to database, etc.)
    print(f"{repo}: {report['analysis_summary']}")
```

### Custom Finding Generation

```python
from comprehensive_repo_analyzer import Finding, Status

# Create custom finding
finding = Finding(
    phase="Custom",
    status=Status.RED,
    title="Custom finding",
    location="custom/path",
    impact="This is a custom analysis",
    recommendation="Do something about it"
)

analyzer.findings.append(finding)
```

## Troubleshooting

**"Cannot fetch repo contents"**
- Ensure repo is public
- Check GitHub API rate limits (60/hour without auth)

**"No findings generated"**
- Repository might be too small or empty
- Check that files exist at: github.com/owner/repo

**"Output file already exists"**
- Tool will overwrite existing files
- Back up before re-running analysis

## Performance Notes

- First run takes 10-30 seconds (fetching and analyzing)
- Subsequent runs use cache where possible
- API rate limit: 60 requests/hour per IP (no auth required)
- To increase rate limit: Add GitHub token to `GITHUB_TOKEN` env variable (5,000/hour)

## Roadmap

### Phase 2 Enhancements
- [ ] Dependency vulnerability scanning (integrate with npm/PyPI APIs)
- [ ] Cyclomatic complexity analysis of sample files
- [ ] Code duplication detection (basic)
- [ ] Performance metrics extraction
- [ ] CI/CD configuration validation

### Phase 3 Enhancements
- [ ] Test coverage extraction from CI logs
- [ ] Code smell detection patterns
- [ ] Architecture diagram extraction
- [ ] Technology debt estimation

### Phase 4 Enhancements  
- [ ] Secret scanning (detect API keys, tokens)
- [ ] Known vulnerability database checks
- [ ] OWASP Top 10 pattern matching
- [ ] Compliance checking (GDPR, HIPAA, etc.)

---

**You now have:** A production-ready analyzer that fits perfectly into your UI component standardization project. Use it to audit codebases before enforcing component standards.

**Next step?** Create the component specification (Phase 2 of UI system), or run analyses on your organization's repos to establish baseline quality metrics.
