# Interactive CLI Guide

## New Feature: Interactive Repo URL Input

The CLI now **prompts for the GitHub repo URL** instead of requiring it as a command-line argument.

---

## How to Use

### Step 1: Run the Script

```bash
python comprehensive_analyzer_cli.py
```

**No arguments needed!** ✨

### Step 2: Enter GitHub Repo URL

You'll see:
```
======================================================================
🔍 COMPREHENSIVE REPOSITORY ANALYZER
======================================================================

Enter the GitHub repository URL:
  Examples: facebook/react
           https://github.com/vuejs/vue
           psf/requests

📦 GitHub repo URL: 
```

**Type one of these formats:**
- `facebook/react` ✅
- `https://github.com/facebook/react` ✅
- `psf/requests` ✅
- `vuejs/vue` ✅

### Step 3: Select Output Format

```
📊 Select output format:
  1. Table (human-readable) - DEFAULT
  2. JSON (structured data)
  3. CSV (spreadsheet analysis)
  4. Mermaid (diagram syntax)
  5. D3 (visualization data)
  6. All formats (generate all 5)

Enter choice (1-6) [default: 1]: 
```

**Choose 1-6:**
- `1` = Just the table (fastest)
- `2` = JSON only
- `3` = CSV only
- `4` = Mermaid diagram
- `5` = D3 visualization
- `6` = All 5 formats at once

---

## Example Session

```
$ python comprehensive_analyzer_cli.py

======================================================================
🔍 COMPREHENSIVE REPOSITORY ANALYZER
======================================================================

Enter the GitHub repository URL:
  Examples: facebook/react
           https://github.com/vuejs/vue
           psf/requests

📦 GitHub repo URL: facebook/react

📊 Select output format:
  1. Table (human-readable) - DEFAULT
  2. JSON (structured data)
  3. CSV (spreadsheet analysis)
  4. Mermaid (diagram syntax)
  5. D3 (visualization data)
  6. All formats (generate all 5)

Enter choice (1-6) [default: 1]: 1

🔍 Analyzing facebook/react...
This may take 10-30 seconds...

[STACK] Detecting tech stack...
[PHASE 1] Understanding & Context Setting...
[PHASE 2] Structural Analysis...
[PHASE 3] Code Quality & Redundancy Analysis...
[PHASE 4] Security Analysis...

[Output displays here]

======================================================================
✨ Analysis complete!
======================================================================

📊 Summary:
   Total findings: 24
   ✅ GREEN: 18
   ⚠️ YELLOW: 3
   🔴 RED: 2

✅ Saved to: react_report.txt
```

---

## New Capabilities

### ✨ Feature 1: Interactive Validation

If you make a typo, the script catches it:

```
📦 GitHub repo URL: invalid
❌ Invalid format. Use 'owner/repo' or full GitHub URL

📦 GitHub repo URL: facebook/react
✅ Accepted!
```

### ✨ Feature 2: Format Menu

Instead of remembering command-line flags, choose from a menu:

```
📊 Select output format:
  1. Table (human-readable) - DEFAULT
  2. JSON (structured data)
  ...
```

### ✨ Feature 3: Generate All Formats

Choose option `6` to generate all 5 output formats at once:

```
Enter choice (1-6) [default: 1]: 6

📋 Generating TABLE output...
✅ Saved to: react_report.txt

📋 Generating JSON output...
✅ Saved to: react_analysis.json

📋 Generating CSV output...
✅ Saved to: react_findings.csv

📋 Generating MERMAID output...
✅ Saved to: react_diagram.md

📋 Generating D3 output...
✅ Saved to: react_visualization.json
```

### ✨ Feature 4: Keyboard Interrupt Support

Press `Ctrl+C` anytime to cancel:

```
🔍 Analyzing facebook/react...
^C
👋 Analysis cancelled by user
```

---

## Comparison: Old vs New

### Old Way (Command Line Args)
```bash
python comprehensive_analyzer_cli.py facebook/react --format json
```
- ❌ Need to remember exact format
- ❌ Easy to make typos
- ❌ One format at a time

### New Way (Interactive)
```bash
python comprehensive_analyzer_cli.py
# Then select from menu
```
- ✅ User-friendly prompts
- ✅ Input validation
- ✅ Can generate multiple formats
- ✅ No command-line arguments to remember

---

## Command-Line Override (Optional)

If you prefer command-line flags, you can still use them:

```bash
# Still works!
python comprehensive_analyzer_cli.py --format json
```

The script will:
1. Prompt for repo URL (interactively)
2. Skip the format menu (use `--format` instead)
3. Run analysis with specified format

---

## Common Use Cases

### Case 1: Quick Analysis (Default)
```
$ python comprehensive_analyzer_cli.py
📦 GitHub repo URL: facebook/react
Enter choice (1-6) [default: 1]: 
[press Enter to use default]
```
**Result:** HTML table report saved

### Case 2: Multiple Formats
```
$ python comprehensive_analyzer_cli.py
📦 GitHub repo URL: vuejs/vue
Enter choice (1-6) [default: 1]: 6
```
**Result:** All 5 formats generated

### Case 3: CSV for Spreadsheet
```
$ python comprehensive_analyzer_cli.py
📦 GitHub repo URL: psf/requests
Enter choice (1-6) [default: 1]: 3
```
**Result:** CSV file ready for Excel/Sheets

### Case 4: Diagram Syntax
```
$ python comprehensive_analyzer_cli.py
📦 GitHub repo URL: angular/angular
Enter choice (1-6) [default: 1]: 4
```
**Result:** Mermaid diagram syntax for GitHub

---

## Error Handling

### Invalid URL Format
```
📦 GitHub repo URL: this-is-wrong
❌ Invalid format. Use 'owner/repo' or full GitHub URL
📦 GitHub repo URL: 
```

### Empty Input
```
📦 GitHub repo URL: 
❌ Please enter a GitHub repo URL
📦 GitHub repo URL: 
```

### Invalid Format Choice
```
Enter choice (1-6) [default: 1]: 99
❌ Invalid choice. Please enter 1-6.
Enter choice (1-6) [default: 1]: 
```

---

## Tips & Tricks

### Tip 1: Press Enter for Defaults
```
Enter choice (1-6) [default: 1]: 
↑ Just press Enter to skip the menu
```

### Tip 2: Copy-Paste GitHub URLs
```
GitHub repo URL: https://github.com/facebook/react
✅ Works! (parses automatically)
```

### Tip 3: Chain Multiple Analyses
```bash
# Run once
python comprehensive_analyzer_cli.py

# Run again with different repo
python comprehensive_analyzer_cli.py
```

### Tip 4: Batch Processing (with loop)
```bash
# Analyze multiple repos
for repo in facebook/react vuejs/vue psf/requests; do
  echo "$repo" | python comprehensive_analyzer_cli.py --format json
done
```

---

## Summary of Changes

| Aspect | Before | After |
|--------|--------|-------|
| **Input Method** | Command-line args | Interactive prompts |
| **Validation** | None | Built-in validation |
| **Format Selection** | Flags (--format) | Menu (1-6) |
| **Multiple Formats** | Run script multiple times | Option 6 (all at once) |
| **User-Friendly** | Technical | Beginner-friendly |

---

## Next Steps

**Try it now:**

```bash
python comprehensive_analyzer_cli.py
```

Just answer the two prompts and you're done! 🚀
