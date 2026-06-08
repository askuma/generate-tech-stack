---
name: generate-tech-stack
description: "Scans any project and generates a visual tech stack HTML page. Detects languages, frameworks, databases, AI SDKs, testing tools, observability, security, and infrastructure from dependency files (requirements.txt, package.json, go.mod, Cargo.toml, pyproject.toml, Dockerfile, docker-compose.yml, .github/workflows). Outputs TECH_STACK.html with: dark-mode design, stat row (total tools / categories / AI backends / data stores), layered architecture diagram, horizontal bar chart summary, and colour-coded tool cards with badges. Trigger: /generate-tech-stack"
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

## Design tokens (dark mode)

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
