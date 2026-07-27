# generate-tech-stack

<!-- mcp-name: io.github.askuma/generate-tech-stack -->

Scan any project and generate a visual `TECH_STACK.html` page — light/dark theme, auto-adapting, zero config.

Works as a **Claude Code skill**, **MCP server**, or **GitHub Copilot Extension**.

**[Live demo →](https://askuma.github.io/generate-tech-stack/)** — generated from
[fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template), unmodified.

![Running generate-tech-stack against fastapi/full-stack-fastapi-template, from pip install to the generated page](https://raw.githubusercontent.com/askuma/generate-tech-stack/main/docs/demo.gif)

*(real CLI output, unscripted — [static screenshot](https://raw.githubusercontent.com/askuma/generate-tech-stack/main/docs/preview.png) if you'd rather not autoplay)*

---

## What it produces

Every generated page contains:

| Section | Description |
|---|---|
| **Stat row** | Total tools · Categories · AI Backends · Data Stores |
| **Architecture diagram** | Layered flow diagram (Consumer → API → AI/NLP → Data/Obs/Frontend) |
| **Bar chart** | Horizontal bars per category, colour-matched |
| **Tool cards** | One card per category; each tool shows a dot, name, description, and badge |
| **Badge legend** | Explains `pip`, `dep`, `optional`, `core`, `deploy`, `ci`, etc. |
| **Footer** | Project name · tool count · generation date |
| **Guided tour** | Spotlight walkthrough of every section, shown automatically the first time a report is opened; replay anytime with the `?` button |
| **Theme toggle** | Sun/moon button next to the tour button switches between dark and light mode |

---

## Repository layout

```
~/.claude/skills/generate-tech-stack/
├── SKILL.md                  ← Claude Code skill definition
├── INSTALL.md                ← detailed per-platform installation guide
├── README.md                 ← this file
├── scripts/
│   └── analyze.py            ← core scanner + HTML renderer (no dependencies)
├── mcp/
│   ├── server.py             ← MCP stdio server (pip install mcp)
│   └── requirements.txt
└── copilot/
    ├── index.js              ← GitHub Copilot Extension (Express)
    ├── package.json
    └── openai_function.json  ← OpenAI / Antigravity function definition
```

---

## Usage

### pip (CLI + MCP server)

```bash
pip install generate-tech-stack-mcp

generate-tech-stack . TECH_STACK.html    # CLI: scan and write the report
generate-tech-stack-mcp                   # stdio MCP server
```

With pip installed, any MCP host config reduces to:

```json
{
  "mcpServers": {
    "generate-tech-stack": { "command": "generate-tech-stack-mcp" }
  }
}
```

### Claude Code

```
/generate-tech-stack
```

Run it from any project directory. The skill calls `scripts/analyze.py` and opens the result in your browser.

### MCP (Claude Desktop, VS Code, Cursor, Zed, Windsurf, Continue)

```bash
pip install mcp
```

Add to your host's MCP config (replace the path with your actual home directory):

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

Then ask: `generate my tech stack` or `/generate-tech-stack`.

**MCP tools exposed:**
- `generate_tech_stack` — scans a project, writes `TECH_STACK.html`, opens in browser
- `list_tech_stack` — returns a JSON summary, no file written

### GitHub Copilot Extension

```bash
cd copilot
npm install
npm start        # listens on port 3000
ngrok http 3000  # expose for GitHub to reach
```

Register a GitHub App with **Copilot Extension** enabled, set the Agent URL to `https://your-url/agent`, and install it on your account. Then in Copilot Chat:

```
@generate-tech-stack /generate-tech-stack
@generate-tech-stack /generate-tech-stack /path/to/project
```

### Command line (standalone)

```bash
python3 ~/.claude/skills/generate-tech-stack/scripts/analyze.py /path/to/project
# output: /path/to/project/TECH_STACK.html

# custom output path:
python3 scripts/analyze.py . ~/Desktop/TECH_STACK.html
```

`analyze.py` has no third-party dependencies — just Python 3.8+.

---

## What gets detected

| Source file | Detected tools |
|---|---|
| `requirements.txt` / `pyproject.toml` | Python packages (web, DB, AI, testing, observability, security…) |
| `package.json` | Node / npm packages (frameworks, frontend, DB drivers, tooling) |
| `go.mod` | Go language |
| `Cargo.toml` | Rust language |
| `pom.xml` / `build.gradle` | Java / Kotlin |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `**/*.py` source | Optional/dynamic SDKs via `importlib.find_spec()` patterns |
| `docker-compose.yml` / `.env` | PostgreSQL, Redis, MongoDB, SQLite connection strings |
| `Dockerfile` | Docker |
| `docker-compose.yml` | Docker Compose |
| `.github/workflows/` | GitHub Actions |
| `.gitlab-ci.yml` | GitLab CI |
| `alembic.ini` | Alembic migrations |
| `nginx.conf` / `Caddyfile` | Reverse proxy |
| `tsconfig.json` / `src/**/*.ts` | TypeScript |

---

## Detected categories

| Category | Colour | Examples |
|---|---|---|
| Language & Runtime | Green | Python, Go, Rust, TypeScript |
| Web / API Framework | Purple | FastAPI, Express, Django, Next.js |
| Database / Storage | Green | SQLAlchemy, Prisma, Redis, ChromaDB |
| AI Guardrail SDKs | Blue | GuardrailsAI, NVIDIA NeMo, Presidio, Lakera |
| NLP / ML | Teal | spaCy, Transformers, Sentence Transformers |
| Observability | Teal | Prometheus, OpenTelemetry, Sentry, Loguru |
| Testing | Yellow | pytest, Jest, Cypress, Playwright |
| Security / Auth | Rose | PyJWT, bcrypt, Authlib, Helmet |
| Infrastructure / Deploy | Orange | Docker, Kubernetes, Celery, Boto3 |
| Frontend / Dashboard | Gray | React, Vue, Tailwind, Recharts |
| Messaging / Comms | Blue | Kafka, RabbitMQ, Socket.io |
| Dev Tools | Gray | ESLint, Prettier, Vite, TypeScript |

---

## Design

Dark by default with a light-mode toggle (top-right corner, no persistence — resets to dark on reload). Fonts: **IBM Plex Sans** (body) + **JetBrains Mono** (code/badges), loaded from Google Fonts. Vanilla JS powers the guided tour and theme toggle only — everything else is plain HTML + CSS. Self-contained single file, opens in any browser offline.

---

## See also

- [INSTALL.md](INSTALL.md) — per-platform setup instructions
- [SKILL.md](SKILL.md) — Claude Code skill specification
