# Agent Quick Start

## 30-Second Start

```bash
python3 repository_analyzer_agent.py
# Enter: facebook/react
# Answer prompts (defaults are fine)
```

## 5-Minute Complete Workflow

```bash
# 1. Run agent
python3 repository_analyzer_agent.py << EOF
facebook/react
yes
1
1
EOF

# 2. Generate visualizations
python3 visualize_mike_analysis.py \
  facebook_react/facebook_react_visualization.json \
  facebook_react/

# 3. Check results
open facebook_react/
open facebook_react/facebook_react_agent_report.json
```

## What You Get

✅ **Instant Analysis** - Comprehensive repository analysis in one command
✅ **Smart Insights** - AI-extracted patterns and gaps
✅ **Recommendations** - Prioritized action items
✅ **Interactive Graphs** - Visualizations with status indicators
✅ **Action Plan** - Personalized to your decisions

## The 6 Steps

| Step | What | Output |
|------|------|--------|
| 1 | Analyze repo | 11 findings (GREEN/YELLOW/RED) |
| 2 | Generate formats | JSON, CSV, Mermaid |
| 3 | Extract insights | Patterns, gaps, health |
| 4 | Recommendations | CRITICAL → HIGH → MEDIUM |
| 5 | Decision points | 3 key questions |
| 6 | Action plan | Personalized steps |

## Command Cheatsheet

### Run Agent
```bash
python3 repository_analyzer_agent.py
```

### Run Agent Silently (No Prompts)
```bash
python3 repository_analyzer_agent.py << EOF
facebook/react
yes
1
1
EOF
```

### Generate Visualization PNG
```bash
python3 visualize_mike_analysis.py \
  facebook_react/facebook_react_visualization.json \
  facebook_react/
```

### Generate All Formats
```bash
python3 graph_generator.py \
  facebook_react/facebook_react_visualization.json \
  facebook_react/
```

### Analyze Multiple Repos
```bash
for repo in facebook/react vuejs/vue django/django; do
  python3 repository_analyzer_agent.py << EOF
$repo
yes
1
1
EOF
done
```

## Decision Points Explained

**Decision 1: Security Report?**
- YES → Detailed security analysis
- NO → Focus on other areas

**Decision 2: Phase Focus?**
- YES → Focus on area with most issues
- NO → Balanced approach

**Decision 3: Approach?**
- 1 = Quick Wins (3-5 items, <1 hour)
- 2 = Comprehensive (full roadmap, 2-4 weeks)

## Output Files

```
facebook_react/
├── facebook_react_agent_report.json      ← Main report with decisions
├── facebook_react_visualization.json     ← Graph data
├── facebook_react_analysis.json          ← Full analysis
├── facebook_react_findings.csv           ← Spreadsheet format
└── facebook_react_diagram.md             ← Mermaid syntax
```

## Next: Generate PNG Diagrams

```bash
python3 visualize_mike_analysis.py \
  facebook_react/facebook_react_visualization.json \
  facebook_react/

# Creates: facebook_react/mike_analysis_hierarchical.png
```

## Troubleshooting

**Module not found?**
```bash
# Make sure you're in the repo directory
cd /Users/deantaylor_2026/corgi-hackathon
python3 repository_analyzer_agent.py
```

**API rate limited?**
```bash
# Set GitHub token for higher limits
export GITHUB_TOKEN=your_token
python3 repository_analyzer_agent.py
```

**Takes too long?**
- First run: 10-30 seconds (normal)
- Large repos: May take longer
- Subsequent runs: Faster

## File Structure

```
corgi-hackathon/
├── repository_analyzer_agent.py      ← Main agent (NEW)
├── agent_insights.py                 ← Intelligence engine (NEW)
├── AGENT_GUIDE.md                    ← Full documentation (NEW)
├── AGENT_QUICKSTART.md               ← This file (NEW)
├── AGENT_IMPLEMENTATION_SUMMARY.md   ← Overview (NEW)
│
├── comprehensive_repo_analyzer.py    ← Core analyzer (existing)
├── comprehensive_analyzer_cli.py     ← CLI (existing)
├── visualize_mike_analysis.py        ← Visualization (existing)
├── graph_generator.py                ← Format exporter (existing)
```

## Common Workflows

### Workflow 1: Analyze & Visualize
```bash
# Analyze
python3 repository_analyzer_agent.py << EOF
facebook/react
yes
1
1
EOF

# Visualize
python3 visualize_mike_analysis.py \
  facebook_react/facebook_react_visualization.json \
  facebook_react/

# View diagram
open facebook_react/mike_analysis_hierarchical.png
```

### Workflow 2: Share with Team
```bash
# Analyze
python3 repository_analyzer_agent.py << EOF
facebook/react
yes
1
1
EOF

# Pack results
zip -r facebook_react_analysis.zip facebook_react/

# Share facebook_react_analysis.zip with team
```

### Workflow 3: Track Progress
```bash
# First analysis (baseline)
python3 repository_analyzer_agent.py << EOF
facebook/react
yes
1
1
EOF

# ... implement recommendations ...

# Second analysis (measure improvement)
python3 repository_analyzer_agent.py << EOF
facebook/react
yes
1
1
EOF

# Compare reports
diff facebook_react/facebook_react_agent_report.json facebook_react/facebook_react_agent_report.json.old
```

## Tips

💡 **Save reports** - Keep old reports to track progress
💡 **Share PDFs** - Convert PNG diagrams to PDF for reports
💡 **Batch analyze** - Use loops for multiple repos
💡 **Version control** - Commit agent reports to track changes
💡 **Automate** - Add to CI/CD for continuous analysis

## More Info

📖 **Full Guide:** See `AGENT_GUIDE.md`
📋 **Implementation:** See `AGENT_IMPLEMENTATION_SUMMARY.md`
💻 **Code:** See `repository_analyzer_agent.py` and `agent_insights.py`

---

**Ready to analyze? Run:** `python3 repository_analyzer_agent.py`
