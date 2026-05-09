import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()


def build_tree(paths: list[str]) -> dict:
    root: dict = {}
    for path in paths:
        node = root
        parts = path.split("/")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = None
    return root


def print_tree(node: dict, prefix: str = "") -> None:
    entries = sorted(node.items(), key=lambda x: (x[1] is None, x[0]))
    for i, (name, children) in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        print(prefix + connector + name + ("/" if children is not None else ""))
        if children is not None:
            print_tree(children, prefix + ("    " if is_last else "│   "))


def build_html_tree(node: dict) -> str:
    entries = sorted(node.items(), key=lambda x: (x[1] is None, x[0]))
    items = []
    for name, children in entries:
        if children is not None:
            inner = build_html_tree(children)
            items.append(
                f'<li class="dir">'
                f'<span class="toggle">▶</span>'
                f'<span class="folder">📁 {name}</span>'
                f'<ul>{inner}</ul>'
                f'</li>'
            )
        else:
            items.append(f'<li class="file">📄 {name}</li>')
    return "".join(items)


def generate_html(repo: str, root: dict, output_path: str) -> None:
    tree_html = build_html_tree(root)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{repo} — File Tree</title>
  <style>
    body {{
      font-family: monospace;
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 2rem;
    }}
    h1 {{ color: #9cdcfe; margin-bottom: 1rem; }}
    ul {{ list-style: none; padding-left: 1.2rem; }}
    li {{ margin: 2px 0; }}
    li.dir > ul {{ display: none; }}
    li.dir.open > ul {{ display: block; }}
    .toggle {{
      cursor: pointer;
      display: inline-block;
      width: 1rem;
      font-size: 0.7rem;
      transition: transform 0.15s;
      user-select: none;
    }}
    li.dir.open > .toggle {{ transform: rotate(90deg); }}
    .folder {{ color: #e5c07b; cursor: pointer; }}
    li.file {{ padding-left: 1.3rem; color: #abb2bf; }}
    #expand-all, #collapse-all {{
      margin-right: 0.5rem;
      padding: 0.3rem 0.8rem;
      background: #2d2d2d;
      color: #9cdcfe;
      border: 1px solid #555;
      border-radius: 4px;
      cursor: pointer;
    }}
    #expand-all:hover, #collapse-all:hover {{ background: #3a3a3a; }}
  </style>
</head>
<body>
  <h1>📦 {repo}/</h1>
  <div style="margin-bottom:1rem">
    <button id="expand-all">Expand all</button>
    <button id="collapse-all">Collapse all</button>
  </div>
  <ul id="root">{tree_html}</ul>
  <script>
    document.querySelectorAll('li.dir').forEach(dir => {{
      const toggle = dir.querySelector(':scope > .toggle');
      const folder = dir.querySelector(':scope > .folder');
      [toggle, folder].forEach(el => {{
        el.addEventListener('click', () => dir.classList.toggle('open'));
      }});
    }});
    document.getElementById('expand-all').addEventListener('click', () => {{
      document.querySelectorAll('li.dir').forEach(d => d.classList.add('open'));
    }});
    document.getElementById('collapse-all').addEventListener('click', () => {{
      document.querySelectorAll('li.dir').forEach(d => d.classList.remove('open'));
    }});
  </script>
</body>
</html>"""
    with open(output_path, "w") as f:
        f.write(html)
    print(f"\nHTML file tree saved to: {output_path}")


def get_file_tree(repo_url: str, token: str | None = None) -> None:
    repo_url = repo_url.rstrip("/").removesuffix(".git")
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]

    headers = {"Authorization": f"token {token}"} if token else {}

    repo_info = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers).json()
    branch = repo_info.get("default_branch", "main")

    tree_resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
        headers=headers,
    ).json()

    if "tree" not in tree_resp:
        print(f"Error fetching tree: {tree_resp.get('message', 'Unknown error')}")
        return

    paths = [item["path"] for item in tree_resp["tree"] if item["type"] == "blob"]
    root = build_tree(paths)

    print(f"{repo}/")
    print_tree(root)

    os.makedirs("Preview", exist_ok=True)
    generate_html(repo, root, f"Preview/{repo}_tree.html")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/willchen96/mike.git"
    github_token = os.getenv("GITHUB_TOKEN")
    get_file_tree(url, token=github_token)
