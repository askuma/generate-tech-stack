---
name: generate-tech-stack
description: >
  FIRE this skill when the user's intent is to discover, list, visualize, document, or summarize
  the technologies used in a software project. This includes all of the following triggers:

  EXPLICIT COMMANDS: /generate-tech-stack; "generate tech stack"; "create tech stack";
  "show tech stack"; "build tech stack"; "make tech stack page"; "tech stack report".

  DISCOVERY / INVENTORY INTENT: user wants to know what libraries, packages, dependencies,
  frameworks, tools, or services a project uses — phrased as: "what libraries does this use",
  "what packages are installed", "what dependencies does this project have", "list all tools",
  "what frameworks are in use", "show me the dependencies", "what's in requirements.txt",
  "scan my project", "audit the stack", "inventory the project", "what's this project built with",
  "what tech does this use", "show all packages", "detect the stack".

  VISUALIZATION / DOCUMENTATION INTENT: user wants an HTML page, visual report, or summary
  document of the project's technology choices — phrased as: "generate a visual tech stack",
  "create a tech stack page", "document the stack", "tech stack diagram", "stack overview",
  "write a tech stack report", "produce a stack summary", "show the project stack visually",
  "generate TECH_STACK.html", "create stack docs".

  DO NOT FIRE for: architecture diagrams, service topology maps, request/data flow diagrams,
  component interaction diagrams, or capacity/throughput analysis — those route to workflow-generator.
  DO NOT FIRE for: code review, dependency vulnerability scanning, or upgrading packages.
---

# generate-tech-stack

Scan the current project and produce a complete visual tech stack page.

## Steps

1. **Locate the project root** — use the current working directory unless the user specified a path.

2. **Run the analyzer**:
   ```bash
   python3 ~/.claude/skills/generate-tech-stack/scripts/analyze.py <project_root> <project_root>/TECH_STACK.html
   ```

3. **Open the output**:
   ```bash
   xdg-open <project_root>/TECH_STACK.html 2>/dev/null || open <project_root>/TECH_STACK.html 2>/dev/null || true
   ```

4. **Report to the user** — include:
   - Number of tools detected and categories found
   - Clickable link to the output file
   - One-line per-category breakdown from the script's stdout

## Output format

The generated HTML must include all of the following sections (the script produces all of them automatically):

1. **Stat row** — large number tiles: Total Tools · Categories · AI Backends (if any) · Data Stores
2. **Architecture diagram** — layered flow:
   - Row 1: Your Application / LLM Application (purple box)
   - Row 2: Web/API framework(s) (green box with auth/middleware subtitle)
   - Row 3: AI SDK boxes side-by-side (blue, one per backend — only if AI SDKs detected)
   - Row 4: Database boxes + Observability + Frontend (dark row)
3. **Bar chart summary** — horizontal bars, one per category, colour-matched
4. **Tool cards grid** — one card per category with:
   - Coloured icon box + category title + tool count in the header
   - Each tool: colour dot · name · description · badge pill
5. **Footer** — project name · tool count · generation date
6. **Guided tour** — a spotlight walkthrough that dims the page and steps through each section
   in turn (Back/Next/Skip), shown automatically the first time a generated report is opened.
   Replayable anytime via the `?` button in the top-right corner.
7. **Theme toggle** — sun/moon button beside the tour button switches between dark (default)
   and light mode.

## Design tokens (default dark theme)

| CSS variable | Value | Usage |
|---|---|---|
| `--bg` | `#0f172a` | Page background |
| `--bg2` | `#111827` | Secondary background |
| `--bg3` | `#161e2e` | Card / chart background |
| `--bg4` | `#1a2535` | Elevated surface |
| `--border` | `#1e293b` | Card / section borders |
| `--border2` | `#263347` | Hover border |
| `--text` | `#f1f5f9` | Primary text |
| `--muted` | `#64748b` | Secondary / label text |
| `--dim` | `#334155` | Footer / divider text |
| `--green` | `#22c55e` | Accent (badge dot, stat highlight) |
| `--mono` | `'JetBrains Mono', monospace` | Code / badge font |
| `--sans` | `'IBM Plex Sans', system-ui, sans-serif` | Body font |

Fonts are loaded from Google Fonts:
```
IBM Plex Sans:wght@300;400;500;600;700
JetBrains Mono:wght@400;500;600
```

Heading `h1`: `color:#f8fafc`, no gradient. Bar chart track: `background:#0a0f1a`.

## Fallback (script not found)

If `~/.claude/skills/generate-tech-stack/scripts/analyze.py` cannot be found:
- Read `requirements.txt`, `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`
- Check for `Dockerfile`, `docker-compose.yml`, `.github/workflows/`, `alembic.ini`
- Identify each tool's category and purpose
- Write `TECH_STACK.html` using the design tokens and section structure above

## Notes

- Always overwrite an existing `TECH_STACK.html` — never ask for confirmation
- Works on Python, Node.js, Go, Rust, Java, Ruby, PHP projects
- The architecture diagram adapts to what is detected: layers are omitted if their category is empty
