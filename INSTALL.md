# generate-tech-stack — Installation Guide

Type `/generate-tech-stack` in any supported tool to get a visual tech stack for your project.

The skill lives at: `~/.claude/skills/generate-tech-stack/`

```
~/.claude/skills/generate-tech-stack/
├── SKILL.md                  ← Claude Code skill definition
├── INSTALL.md                ← this file
├── scripts/
│   └── analyze.py            ← core scanner + HTML renderer
├── mcp/
│   ├── server.py             ← MCP stdio server
│   └── requirements.txt
└── copilot/
    ├── index.js              ← GitHub Copilot Extension (Express)
    ├── package.json
    └── openai_function.json  ← Antigravity / OpenAI function def
```

---

## Claude Code

The skill is already installed. Just use:

```
/generate-tech-stack
```

To reinstall or update:

```bash
# Clone or copy the skill files
mkdir -p ~/.claude/skills/generate-tech-stack/{scripts,mcp,copilot}

# Core analyzer
curl -L https://raw.githubusercontent.com/yourorg/generate-tech-stack/main/scripts/analyze.py \
     -o ~/.claude/skills/generate-tech-stack/scripts/analyze.py

# Skill definition
curl -L https://raw.githubusercontent.com/yourorg/generate-tech-stack/main/SKILL.md \
     -o ~/.claude/skills/generate-tech-stack/SKILL.md
```

---

## MCP (Claude Desktop, VS Code, Cursor, Zed, Continue, Antigravity, Windsurf)

Any host that supports the [Model Context Protocol](https://modelcontextprotocol.io) can use the MCP server.

**Install the dependency:**
```bash
pip install mcp
```

**Configure your MCP host** — replace `/home/<you>` with your actual home directory:

### Claude Desktop
`~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)  
`%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "generate-tech-stack": {
      "command": "python3",
      "args": ["/home/<you>/.claude/skills/generate-tech-stack/mcp/server.py"]
    }
  }
}
```

### VS Code (`.vscode/mcp.json` or user settings)
```json
{
  "servers": {
    "generate-tech-stack": {
      "type": "stdio",
      "command": "python3",
      "args": ["/home/<you>/.claude/skills/generate-tech-stack/mcp/server.py"]
    }
  }
}
```

### Cursor (`~/.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "generate-tech-stack": {
      "command": "python3",
      "args": ["/home/<you>/.claude/skills/generate-tech-stack/mcp/server.py"]
    }
  }
}
```

### Zed (`.zed/settings.json`)
```json
{
  "context_servers": {
    "generate-tech-stack": {
      "command": {
        "path": "python3",
        "args": ["/home/<you>/.claude/skills/generate-tech-stack/mcp/server.py"]
      }
    }
  }
}
```

**Restart your tool, then use:**
```
/generate-tech-stack
# or:
"generate my tech stack"
"scan this project and show all tools visually"
```

**MCP tools exposed:**
- `generate_tech_stack` — scans project, writes `TECH_STACK.html`, opens in browser
- `list_tech_stack` — returns JSON summary, no file written

---

## Antigravity / OpenAI-compatible tools

Register the function definition from `copilot/openai_function.json` in your assistant config.
When the model calls `generate_tech_stack`, execute:

```bash
python3 ~/.claude/skills/generate-tech-stack/scripts/analyze.py <project_dir> <output_file>
```

---

## GitHub Copilot Extension

The Copilot Extension is a GitHub App that you deploy as a small Express server.

**Prerequisites:**
- GitHub account with Copilot access
- A public HTTPS endpoint (use [ngrok](https://ngrok.com) for local dev)

**Start the server:**
```bash
cd ~/.claude/skills/generate-tech-stack/copilot
npm install
npm start   # listens on port 3000
```

**For local dev, expose it:**
```bash
ngrok http 3000
# copy the https://xxxx.ngrok.io URL
```

**Register the GitHub App:**
1. GitHub → Settings → Developer settings → GitHub Apps → New GitHub App
2. Set **Homepage URL** and **Callback URL** to your ngrok/deployment URL
3. Enable **Copilot Extension** and set **Agent URL**: `https://your-url/agent`
4. Permissions: `Copilot chat` → Read & Write
5. Install the app on your account or organisation

**Usage** (in GitHub Copilot Chat):
```
@generate-tech-stack /generate-tech-stack
@generate-tech-stack /generate-tech-stack /path/to/project
```

---

## Quick test (any platform)

Run the analyzer directly to verify it works:

```bash
python3 ~/.claude/skills/generate-tech-stack/scripts/analyze.py . ~/TECH_STACK.html
# then open ~/TECH_STACK.html in your browser
```

---

## What gets detected

| Source file | Detected tools |
|---|---|
| `requirements.txt` / `pyproject.toml` | Python packages |
| `package.json` | Node.js / npm packages |
| `go.mod` | Go language |
| `Cargo.toml` | Rust language |
| `pom.xml` / `build.gradle` | Java / Kotlin |
| `Gemfile` | Ruby language |
| `composer.json` | PHP language |
| `Dockerfile` | Docker |
| `docker-compose.yml` | Docker Compose |
| `.github/workflows/` | GitHub Actions |
| `.gitlab-ci.yml` | GitLab CI |
| `alembic.ini` | Alembic migrations |
| `nginx.conf` / `Caddyfile` | Reverse proxy |
| `tsconfig.json` / `src/**/*.ts` | TypeScript |

## Output sections

Every generated `TECH_STACK.html` includes:

1. **Stat row** — Total Tools · Categories · AI Backends · Data Stores
2. **Architecture diagram** — layered flow adapted to what's detected
3. **Bar chart** — horizontal bars per category, colour-matched
4. **Tool cards** — one card per category, each tool with dot · name · desc · badge
5. **Guided tour** — spotlight walkthrough shown automatically on first open, replayable via the
   `?` button in the top-right corner
