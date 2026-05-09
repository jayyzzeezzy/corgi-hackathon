# Repository Analyzer Agent Guide

## Overview

The **Repository Analyzer Agent** is an intelligent orchestrator that automates the entire analysis workflow:

```
GitHub URL → Analysis → Insights → Recommendations → Action Plan
```

Instead of manually running individual scripts and making decisions, the agent handles everything and guides you through decision points.

## Features

✨ **Smart Orchestration**
- Analyzes repository (4-phase comprehensive analysis)
- Generates all visualization formats automatically
- Extracts insights and patterns
- Makes data-driven recommendations

🎯 **Interactive Guidance**
- Presents critical findings upfront
- Asks for user input on decisions
- Creates personalized action plans
- Prioritizes fixes by impact

📊 **Complete Output**
- Interactive graph visualization data
- CSV findings for spreadsheets
- Mermaid diagram syntax
- Full analysis JSON
- Agent decision report

## Usage

### Basic Usage

```bash
python3 repository_analyzer_agent.py
```

Then enter a GitHub repository URL when prompted:
```
📦 GitHub repo URL: facebook/react
```

Or pass the URL directly:
```bash
echo "facebook/react" | python3 repository_analyzer_agent.py
```

### Example Workflows

#### Example 1: Analyze a React Repository
```bash
python3 repository_analyzer_agent.py
# When prompted: facebook/react
```

#### Example 2: Analyze with Full GitHub URL
```bash
python3 repository_analyzer_agent.py
# When prompted: https://github.com/vuejs/vue
```

#### Example 3: Analyze from Bash Script
```bash
#!/bin/bash
REPO="django/django"

python3 repository_analyzer_agent.py << EOF
$REPO
yes
2
1
EOF
```

## Agent Workflow

### Step 1: Repository Analysis (10-30 seconds)
The agent analyzes the repository across 4 phases:
- **Phase 1: Understanding** - File inventory, dependencies, tech stack
- **Phase 2: Structural** - Code organization, directory structure
- **Phase 3: Quality** - Testing, documentation, code standards
- **Phase 4: Security** - Security configuration, scanning, secrets management

### Step 2: Visualization Generation
Automatically generates:
- `{repo}_visualization.json` - Interactive graph data
- `{repo}_analysis.json` - Complete analysis
- `{repo}_findings.csv` - Spreadsheet-ready findings
- `{repo}_diagram.md` - Mermaid diagram syntax

### Step 3: Insight Extraction
Agent identifies:
- Overall codebase health
- Strongest and weakest areas
- Critical capability gaps
- Patterns and trends

Example insights:
```
• Overall codebase health is STRONG (75% good)
• 1 CRITICAL issue requires immediate attention
• Weakest area: 4: Security (3 issues)
• Strongest area: 1: Understanding (3 issues)
• ⚠️ TESTING: No automated test configuration found
```

### Step 4: Recommendations
Agent generates prioritized recommendations:

**[CRITICAL]**
- High-impact, urgent issues
- Must fix for stability/security

**[HIGH]**
- Important but can be planned
- Usually low effort

**[MEDIUM]**
- Nice-to-have improvements
- Quick wins

### Step 5: Decision Points
Agent asks you to make key decisions:

1. **Security Report** - Want detailed security analysis?
2. **Phase Focus** - Which phase to focus on first?
3. **Approach** - Quick wins or comprehensive plan?

### Step 6: Action Plan
Agent generates personalized plan based on your decisions:
```
Approach: Quick Wins
Focus Phase: 4: Security

ACTION PLAN (4 items):

1. [CRITICAL] Enable Automated Security Scanning
   Action: Enable Dependabot or Snyk
   Expected Impact: Detects vulnerabilities before production

2. [HIGH] Add Code Style Configuration
   Action: Add .eslintrc or pylintrc
   Expected Impact: Ensures consistent code quality
```

### Step 7: Output Files
All results saved to repo folder:
```
facebook_react/
├── facebook_react_agent_report.json     # Agent decision report
├── facebook_react_visualization.json    # Interactive graph
├── facebook_react_analysis.json         # Full analysis
├── facebook_react_findings.csv          # CSV export
└── facebook_react_diagram.md            # Mermaid diagram
```

## Output Files Explained

### agent_report.json
```json
{
  "repository": "facebook/react",
  "analysis_summary": { ... },
  "insights": {
    "top_insights": [ ... ],
    "phase_health": { ... },
    "critical_gaps": [ ... ],
    "patterns": [ ... ]
  },
  "recommendations": [ ... ],
  "user_decisions": {
    "security_report": true,
    "focus_phase": "4: Security",
    "approach": "quick_wins"
  },
  "action_plan": { ... }
}
```

### visualization.json
Ready-to-visualize graph format:
```json
{
  "nodes": [
    {"id": "repo", "label": "facebook/react", "type": "repo", "status": "neutral"},
    {"id": "phase_1", "label": "1: Understanding", "type": "phase", "status": "neutral"},
    {"id": "finding_0", "label": "File inventory...", "type": "finding", "status": "green"}
  ],
  "links": [
    {"source": "repo", "target": "phase_1"},
    {"source": "phase_1", "target": "finding_0"}
  ]
}
```

Use with visualization scripts:
```bash
python3 visualize_mike_analysis.py facebook_react/facebook_react_visualization.json facebook_react/
```

## Creating Interactive Visualizations

After agent completes:

```bash
# Generate PNG diagram
python3 visualize_mike_analysis.py \
  facebook_react/facebook_react_visualization.json \
  facebook_react/

# Generate multi-format exports
python3 graph_generator.py \
  facebook_react/facebook_react_visualization.json \
  facebook_react/
```

## Integration Examples

### Example 1: Batch Analysis
```bash
#!/bin/bash
REPOS=("facebook/react" "vuejs/vue" "django/django")

for repo in "${REPOS[@]}"; do
  echo "📊 Analyzing $repo..."
  python3 repository_analyzer_agent.py << EOF
$repo
yes
1
1
EOF
done

echo "✅ Batch analysis complete!"
```

### Example 2: CI/CD Pipeline
```yaml
# .github/workflows/analyze.yml
name: Repository Analysis
on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install requests
      - run: python3 repository_analyzer_agent.py << EOF
              ${{ github.repository }}
              yes
              1
              1
              EOF
      - uses: actions/upload-artifact@v2
        with:
          name: analysis-results
          path: |
            *_agent_report.json
            *_visualization.json
            *_diagram.md
```

### Example 3: Web Integration
```python
from repository_analyzer_agent import RepositoryAnalyzerAgent

# In your Flask/FastAPI app
@app.post("/analyze")
def analyze_repo(url: str):
    agent = RepositoryAnalyzerAgent(url)
    report = agent.run()
    
    # Return results
    return {
        "status": "complete",
        "report": report,
        "visualization_url": f"/files/{agent.repo_folder}"
    }
```

## Decision Guide

### Decision 1: Security Report
- **Yes** - Generate detailed security analysis (shows all security findings)
- **No** - Skip detailed security analysis (focus on other areas)

### Decision 2: Phase Focus
- **Yes** - Create action plan focused on the phase with most issues
- **No** - Balanced approach addressing all phases

### Decision 3: Approach
- **Quick Wins** - 3-5 high-impact items you can fix in <1 hour
- **Comprehensive** - Full roadmap for 2-4 weeks of work

## Tips & Best Practices

✅ **Do**
- Run agent weekly to track improvements
- Share agent reports with your team
- Use decision points to align on priorities
- Implement CRITICAL recommendations first
- Track progress: rerun agent after changes

❌ **Don't**
- Skip CRITICAL findings - they indicate real problems
- Try to implement everything at once - prioritize
- Ignore recommendations without understanding them
- Use outdated analysis - repositories change

## Troubleshooting

### "Module not found: comprehensive_repo_analyzer"
```bash
# Make sure you're in the repo directory with all scripts
cd /path/to/corgi-hackathon
python3 repository_analyzer_agent.py
```

### "GitHub API rate limited"
Agent uses public GitHub API (60 requests/hour unauthenticated).
For higher limits, set environment variable:
```bash
export GITHUB_TOKEN=your_token_here
python3 repository_analyzer_agent.py
```

### Agent takes too long
- First run is slower (10-30 seconds) while analyzing
- Subsequent runs are faster
- Large repositories (10k+ files) may take longer

## Next Steps

1. **Run the agent** on your repository
2. **Review recommendations** from agent report
3. **Use decision points** to prioritize
4. **Generate visualizations** to share with team
5. **Implement action plan** items
6. **Rerun agent** to measure improvements

## Files Generated

| File | Purpose | Format |
|------|---------|--------|
| agent_report.json | Complete agent analysis + decisions | JSON |
| visualization.json | Interactive graph data | JSON |
| analysis.json | Full detailed analysis | JSON |
| findings.csv | Findings in spreadsheet format | CSV |
| diagram.md | Mermaid diagram syntax | Markdown |

---

**Happy analyzing! 🚀**
