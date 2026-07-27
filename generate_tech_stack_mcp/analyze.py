#!/usr/bin/env python3
"""
generate-tech-stack — project analyzer
Scans a project directory, detects all tools/libraries, and writes TECH_STACK.html.

Usage:
    python3 analyze.py [project_dir] [output_file]
"""

import datetime
import json
import re
import sys
from pathlib import Path


# ── Category metadata ─────────────────────────────────────────────────────────

CATEGORY_META = {
    "language":      {"icon": "🐍", "label": "Language & Runtime",      "color": "green"},
    "web":           {"icon": "🌐", "label": "Web / API Framework",     "color": "purple"},
    "database":      {"icon": "🗄️",  "label": "Database / Storage",     "color": "green"},
    "ai_sdk":        {"icon": "🧠", "label": "AI Guardrail SDKs",       "color": "blue"},
    "nlp":           {"icon": "📝", "label": "NLP / ML",                "color": "teal"},
    "testing":       {"icon": "🧪", "label": "Testing",                 "color": "yellow"},
    "observability": {"icon": "📊", "label": "Observability",           "color": "teal"},
    "security":      {"icon": "🔐", "label": "Security / Auth",         "color": "rose"},
    "infra":         {"icon": "🚀", "label": "Infrastructure / Deploy", "color": "orange"},
    "frontend":      {"icon": "🖥️",  "label": "Frontend / Dashboard",  "color": "gray"},
    "messaging":     {"icon": "📬", "label": "Messaging / Comms",      "color": "blue"},
    "devtools":      {"icon": "🛠️",  "label": "Dev Tools",             "color": "gray"},
    "other":         {"icon": "📦", "label": "Other Libraries",        "color": "gray"},
}

# icon_bg, dot_color, title_color
COLOR_CSS = {
    "green":  ("#14532d", "#16a34a", "#4ade80"),
    "purple": ("#2e1065", "#7c3aed", "#a78bfa"),
    "blue":   ("#1e3a5f", "#2563eb", "#60a5fa"),
    "yellow": ("#422006", "#d97706", "#fbbf24"),
    "teal":   ("#134e4a", "#0d9488", "#2dd4bf"),
    "rose":   ("#4c0519", "#e11d48", "#fb7185"),
    "orange": ("#431407", "#ea580c", "#fb923c"),
    "gray":   ("#1e293b", "#6b7280", "#9ca3af"),
}

# badge bg, badge fg
BADGE_CSS = {
    "pip":      ("#1e293b", "#94a3b8"),
    "dep":      ("#14532d", "#86efac"),
    "devDep":   ("#1e1b4b", "#a5b4fc"),
    "optional": ("#1e293b", "#64748b"),
    "core":     ("#14532d", "#86efac"),
    "lang":     ("#431407", "#fdba74"),
    "deploy":   ("#3b1f0f", "#fdba74"),
    "prod":     ("#1e293b", "#64748b"),
    "ci":       ("#1e1b4b", "#a5b4fc"),
    "tool":     ("#1e293b", "#94a3b8"),
}

# Proper display names for pip package names
DISPLAY_NAMES = {
    "fastapi":                "FastAPI",
    "flask":                  "Flask",
    "django":                 "Django",
    "starlette":              "Starlette",
    "uvicorn":                "Uvicorn",
    "gunicorn":               "Gunicorn",
    "httpx":                  "httpx",
    "aiohttp":                "aiohttp",
    "requests":               "Requests",
    "pydantic":               "Pydantic",
    "aiofiles":               "aiofiles",
    "tornado":                "Tornado",
    "sanic":                  "Sanic",
    "sqlalchemy":             "SQLAlchemy",
    "alembic":                "Alembic",
    "psycopg2":               "psycopg2",
    "psycopg2-binary":        "PostgreSQL (psycopg2)",
    "psycopg":                "psycopg3",
    "pymysql":                "PyMySQL",
    "motor":                  "Motor",
    "pymongo":                "PyMongo",
    "redis":                  "Redis",
    "aioredis":               "aioredis",
    "elasticsearch":          "Elasticsearch",
    "tortoise-orm":           "Tortoise ORM",
    "peewee":                 "Peewee",
    "databases":              "databases",
    "asyncpg":                "asyncpg",
    "guardrails-ai":          "GuardrailsAI",
    "guardrails_ai":          "GuardrailsAI",
    "nemoguardrails":         "NVIDIA NeMo",
    "presidio-analyzer":      "Presidio Analyzer",
    "presidio-anonymizer":    "Presidio Anonymizer",
    "openai":                 "OpenAI",
    "anthropic":              "Anthropic",
    "transformers":           "Transformers",
    "torch":                  "PyTorch",
    "tensorflow":             "TensorFlow",
    "keras":                  "Keras",
    "langchain":              "LangChain",
    "langchain-core":         "LangChain Core",
    "langchain-community":    "LangChain Community",
    "llama-index":            "LlamaIndex",
    "llama_index":            "LlamaIndex",
    "spacy":                  "spaCy",
    "nltk":                   "NLTK",
    "sentence-transformers":  "Sentence Transformers",
    "scikit-learn":           "scikit-learn",
    "numpy":                  "NumPy",
    "pandas":                 "Pandas",
    "cohere":                 "Cohere",
    "google-generativeai":    "Google Gemini",
    "mistralai":              "Mistral AI",
    "tiktoken":               "tiktoken",
    "chromadb":               "ChromaDB",
    "pinecone-client":        "Pinecone",
    "weaviate-client":        "Weaviate",
    "qdrant-client":          "Qdrant",
    "faiss-cpu":              "FAISS",
    "pytest":                 "pytest",
    "pytest-asyncio":         "pytest-asyncio",
    "pytest-cov":             "pytest-cov",
    "pytest-mock":            "pytest-mock",
    "hypothesis":             "Hypothesis",
    "factory-boy":            "factory-boy",
    "faker":                  "Faker",
    "locust":                 "Locust",
    "coverage":               "Coverage",
    "prometheus-client":      "Prometheus Client",
    "python-json-logger":     "python-json-logger",
    "opentelemetry-api":      "OpenTelemetry API",
    "opentelemetry-sdk":      "OpenTelemetry SDK",
    "sentry-sdk":             "Sentry",
    "datadog":                "Datadog",
    "elastic-apm":            "Elastic APM",
    "loguru":                 "Loguru",
    "cryptography":           "Cryptography",
    "pyjwt":                  "PyJWT",
    "passlib":                "Passlib",
    "python-jose":            "python-jose",
    "bcrypt":                 "bcrypt",
    "paramiko":               "Paramiko",
    "authlib":                "Authlib",
    "celery":                 "Celery",
    "dramatiq":               "Dramatiq",
    "boto3":                  "Boto3 (AWS)",
    "google-cloud-storage":   "GCS",
    "azure-storage-blob":     "Azure Blob",
    "kubernetes":             "Kubernetes",
    "pika":                   "Pika (RabbitMQ)",
    "kafka-python":           "kafka-python",
    "aiokafka":               "aiokafka",
    "pyyaml":                 "PyYAML",
    "toml":                   "TOML",
    "click":                  "Click",
    "typer":                  "Typer",
    "rich":                   "Rich",
    "jinja2":                 "Jinja2",
    "python-dotenv":          "python-dotenv",
    "pillow":                 "Pillow",
    "websockets":             "websockets",
}


# ── Package maps ──────────────────────────────────────────────────────────────

PYTHON_MAP = {
    # Web
    "fastapi":             ("web", "REST API framework"),
    "flask":               ("web", "Micro web framework"),
    "django":              ("web", "Full-stack web framework"),
    "starlette":           ("web", "ASGI toolkit"),
    "uvicorn":             ("web", "ASGI server"),
    "gunicorn":            ("web", "WSGI HTTP server"),
    "httpx":               ("web", "Async HTTP client"),
    "aiohttp":             ("web", "Async HTTP client/server"),
    "requests":            ("web", "HTTP client"),
    "pydantic":            ("web", "Data validation"),
    "aiofiles":            ("web", "Async file I/O"),
    "tornado":             ("web", "Non-blocking web framework"),
    "sanic":               ("web", "Async web framework"),
    # Database
    "sqlalchemy":          ("database", "ORM / query builder"),
    "alembic":             ("database", "DB migrations"),
    "psycopg2":            ("database", "PostgreSQL adapter"),
    "psycopg2-binary":     ("database", "PostgreSQL adapter"),
    "psycopg":             ("database", "PostgreSQL adapter v3"),
    "pymysql":             ("database", "MySQL adapter"),
    "motor":               ("database", "Async MongoDB driver"),
    "pymongo":             ("database", "MongoDB driver"),
    "redis":               ("database", "Redis client"),
    "aioredis":            ("database", "Async Redis client"),
    "elasticsearch":       ("database", "Elasticsearch client"),
    "tortoise-orm":        ("database", "Async ORM"),
    "peewee":              ("database", "Simple ORM"),
    "databases":           ("database", "Async DB queries"),
    "asyncpg":             ("database", "Async PostgreSQL driver"),
    # AI / ML guardrail SDKs
    "guardrails-ai":       ("ai_sdk", "Composable AI validators"),
    "guardrails_ai":       ("ai_sdk", "Composable AI validators"),
    "nemoguardrails":      ("ai_sdk", "Colang state machine"),
    "presidio-analyzer":   ("ai_sdk", "PII detection"),
    "presidio-anonymizer": ("nlp",    "PII redaction engine"),
    "openai":              ("ai_sdk", "OpenAI API client"),
    "anthropic":           ("ai_sdk", "Anthropic API client"),
    "transformers":        ("ai_sdk", "Hugging Face Transformers"),
    "torch":               ("ai_sdk", "PyTorch"),
    "tensorflow":          ("ai_sdk", "TensorFlow"),
    "keras":               ("ai_sdk", "Deep learning API"),
    "langchain":           ("ai_sdk", "LLM orchestration"),
    "langchain-core":      ("ai_sdk", "LangChain core"),
    "langchain-community": ("ai_sdk", "LangChain integrations"),
    "llama-index":         ("ai_sdk", "LlamaIndex RAG"),
    "llama_index":         ("ai_sdk", "LlamaIndex RAG"),
    "spacy":               ("nlp", "NLP pipeline"),
    "nltk":                ("nlp", "Natural language toolkit"),
    "sentence-transformers": ("nlp", "Sentence embeddings"),
    "scikit-learn":        ("ai_sdk", "Machine learning"),
    "numpy":               ("ai_sdk", "Numerical computing"),
    "pandas":              ("ai_sdk", "Data manipulation"),
    "cohere":              ("ai_sdk", "Cohere API client"),
    "google-generativeai": ("ai_sdk", "Google Gemini client"),
    "mistralai":           ("ai_sdk", "Mistral API client"),
    "tiktoken":            ("ai_sdk", "OpenAI tokenizer"),
    "chromadb":            ("database", "Vector database"),
    "pinecone-client":     ("database", "Pinecone vector DB"),
    "weaviate-client":     ("database", "Weaviate vector DB"),
    "qdrant-client":       ("database", "Qdrant vector DB"),
    "faiss-cpu":           ("ai_sdk", "FAISS similarity search"),
    # Testing
    "pytest":              ("testing", "Test runner"),
    "pytest-asyncio":      ("testing", "Async test support"),
    "pytest-cov":          ("testing", "Coverage reporting"),
    "pytest-mock":         ("testing", "Mock helpers"),
    "hypothesis":          ("testing", "Property-based testing"),
    "factory-boy":         ("testing", "Test fixtures"),
    "faker":               ("testing", "Fake data generator"),
    "locust":              ("testing", "Load testing"),
    "coverage":            ("testing", "Code coverage"),
    # Observability
    "prometheus-client":   ("observability", "Prometheus metrics"),
    "python-json-logger":  ("observability", "Structured JSON logging"),
    "opentelemetry-api":   ("observability", "OpenTelemetry tracing"),
    "opentelemetry-sdk":   ("observability", "OpenTelemetry SDK"),
    "sentry-sdk":          ("observability", "Error tracking"),
    "datadog":             ("observability", "Datadog APM"),
    "elastic-apm":         ("observability", "Elastic APM"),
    "loguru":              ("observability", "Modern logging"),
    # Security
    "cryptography":        ("security", "Cryptographic primitives"),
    "pyjwt":               ("security", "JSON Web Tokens"),
    "passlib":             ("security", "Password hashing"),
    "python-jose":         ("security", "JOSE / JWT"),
    "bcrypt":              ("security", "bcrypt hashing"),
    "paramiko":            ("security", "SSH client"),
    "authlib":             ("security", "OAuth / OIDC"),
    # Infra / messaging
    "celery":              ("infra", "Distributed task queue"),
    "dramatiq":            ("infra", "Task queue"),
    "boto3":               ("infra", "AWS SDK"),
    "google-cloud-storage": ("infra", "GCS client"),
    "azure-storage-blob":  ("infra", "Azure Blob Storage"),
    "kubernetes":          ("infra", "Kubernetes client"),
    "pika":                ("messaging", "RabbitMQ client"),
    "kafka-python":        ("messaging", "Kafka client"),
    "aiokafka":            ("messaging", "Async Kafka client"),
    # Other
    "pyyaml":              ("other", "YAML parser"),
    "toml":                ("other", "TOML parser"),
    "click":               ("other", "CLI framework"),
    "typer":               ("other", "CLI framework"),
    "rich":                ("other", "Terminal formatting"),
    "jinja2":              ("other", "Template engine"),
    "python-dotenv":       ("other", "Env var loader"),
    "pillow":              ("other", "Image processing"),
    "websockets":          ("other", "WebSocket library"),
}

NODE_MAP = {
    "express":              ("web", "Web framework"),
    "fastify":              ("web", "Fast web framework"),
    "koa":                  ("web", "Middleware framework"),
    "next":                 ("frontend", "React framework"),
    "nuxt":                 ("frontend", "Vue framework"),
    "remix":                ("frontend", "Full-stack React"),
    "axios":                ("web", "HTTP client"),
    "node-fetch":           ("web", "Fetch API for Node"),
    "react":                ("frontend", "UI component library"),
    "react-dom":            ("frontend", "React DOM renderer"),
    "react-scripts":        ("frontend", "CRA build toolchain"),
    "vue":                  ("frontend", "Progressive UI framework"),
    "svelte":               ("frontend", "Compiled UI framework"),
    "vite":                 ("devtools", "Build tool"),
    "webpack":              ("devtools", "Module bundler"),
    "tailwindcss":          ("frontend", "Utility CSS framework"),
    "recharts":             ("frontend", "Chart components"),
    "chart.js":             ("frontend", "Canvas charts"),
    "d3":                   ("frontend", "Data visualisation"),
    "lucide-react":         ("frontend", "Icon library"),
    "framer-motion":        ("frontend", "Animation library"),
    "prisma":               ("database", "Type-safe ORM"),
    "mongoose":             ("database", "MongoDB ODM"),
    "pg":                   ("database", "PostgreSQL client"),
    "mysql2":               ("database", "MySQL client"),
    "redis":                ("database", "Redis client"),
    "ioredis":              ("database", "Redis client"),
    "sequelize":            ("database", "Multi-dialect ORM"),
    "knex":                 ("database", "Query builder"),
    "typeorm":              ("database", "TypeScript ORM"),
    "drizzle-orm":          ("database", "TypeScript ORM"),
    "jest":                 ("testing", "Test runner"),
    "vitest":               ("testing", "Vite-native test runner"),
    "mocha":                ("testing", "Test framework"),
    "chai":                 ("testing", "Assertion library"),
    "cypress":              ("testing", "E2E testing"),
    "playwright":           ("testing", "Browser automation"),
    "supertest":            ("testing", "HTTP assertion"),
    "openai":               ("ai_sdk", "OpenAI API client"),
    "@anthropic-ai/sdk":    ("ai_sdk", "Anthropic API client"),
    "langchain":            ("ai_sdk", "LLM orchestration"),
    "@langchain/core":      ("ai_sdk", "LangChain core"),
    "jsonwebtoken":         ("security", "JSON Web Tokens"),
    "bcrypt":               ("security", "Password hashing"),
    "passport":             ("security", "Auth middleware"),
    "helmet":               ("security", "HTTP security headers"),
    "express-rate-limit":   ("security", "Rate limiting"),
    "pino":                 ("observability", "Structured logger"),
    "winston":              ("observability", "Logging library"),
    "morgan":               ("observability", "HTTP request logger"),
    "bull":                 ("infra", "Job queue"),
    "bullmq":               ("infra", "Job queue"),
    "socket.io":            ("messaging", "WebSocket server"),
    "ws":                   ("messaging", "WebSocket library"),
    "aws-sdk":              ("infra", "AWS SDK"),
    "@aws-sdk/client-s3":   ("infra", "AWS S3 client"),
    "dotenv":               ("other", "Env var loader"),
    "zod":                  ("other", "Schema validation"),
    "typescript":           ("devtools", "TypeScript compiler"),
    "eslint":               ("devtools", "Linter"),
    "prettier":             ("devtools", "Code formatter"),
    "esbuild":              ("devtools", "Fast bundler"),
    "turbo":                ("devtools", "Monorepo build tool"),
}

# Packages detected via importlib.find_spec() or import_module() in source files
FIND_SPEC_MAP = {
    "guardrails":         ("ai_sdk", "GuardrailsAI",      "Composable AI validators"),
    "nemoguardrails":     ("ai_sdk", "NVIDIA NeMo",       "Colang state machine"),
    "presidio_analyzer":  ("ai_sdk", "Presidio Analyzer", "PII detection"),
    "presidio":           ("ai_sdk", "Presidio Analyzer", "PII analysis"),
    "spacy":              ("nlp",    "spaCy",              "NLP pipeline"),
    "transformers":       ("ai_sdk", "Transformers",      "Hugging Face Transformers"),
    "torch":              ("ai_sdk", "PyTorch",            "Deep learning"),
    "openai":             ("ai_sdk", "OpenAI",             "OpenAI API client"),
    "anthropic":          ("ai_sdk", "Anthropic",          "Anthropic API client"),
    "langchain":          ("ai_sdk", "LangChain",          "LLM orchestration"),
}


# ── Scanners ──────────────────────────────────────────────────────────────────

# Directories that contain third-party or generated code, never the project's own
# stack. Scanning them would report every installed dependency's dependencies
# (e.g. a local venv or vendored site-packages would add dozens of false tools).
EXCLUDED_DIRS = frozenset({
    ".git", ".hg", ".svn",
    "node_modules", "bower_components",
    "site-packages", "dist-packages",
    "venv", ".venv", "env", "virtualenv",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".nox",
    "dist", "build", "target", ".next", ".nuxt", ".output",
    "vendor", "third_party", ".terraform",
    "htmlcov", "coverage", ".cache",
})


def _iter_files(root: Path, pattern: str):
    """rglob that skips vendored/venv/build directories."""
    for p in root.rglob(pattern):
        parents = p.relative_to(root).parts[:-1]
        if any(d in EXCLUDED_DIRS or d.endswith(".egg-info") for d in parents):
            continue
        yield p


def _normalize(name: str) -> str:
    return name.lower().replace("-", "").replace("_", "").replace(" ", "")


def _add_tool(tools: dict, cat: str, name: str, desc: str, badge: str) -> None:
    """Add a tool to the category, skipping if a normalized-equivalent entry exists."""
    tools.setdefault(cat, [])
    norm = _normalize(name)
    if any(_normalize(t["name"]) == norm for t in tools[cat]):
        return
    tools[cat].append({"name": name, "desc": desc, "badge": badge})


def scan_python(root: Path) -> dict:
    tools: dict = {}
    # Root manifests + one level of subdirectories (monorepos: backend/, api/, …)
    req_candidates = [
        root / f for f in ["requirements.txt", "requirements-dev.txt", "requirements/base.txt"]
    ] + [p for p in root.glob("*/requirements.txt") if p.parent.name not in EXCLUDED_DIRS]
    for fpath in req_candidates:
        if not fpath.exists():
            continue
        for line in fpath.read_text().splitlines():
            line = line.strip()
            if not line:
                continue

            if line.startswith("#"):
                # Detect commented-out package lines: # package>=version
                m = re.match(r'^#\s*([\w][\w\-\.]*)\s*[>=<!\[]', line)
                if m:
                    pkg = m.group(1).lower()
                    if pkg in PYTHON_MAP:
                        cat, desc = PYTHON_MAP[pkg]
                        display = DISPLAY_NAMES.get(pkg, pkg)
                        _add_tool(tools, cat, display, desc, "optional")
                # Detect PostgreSQL from psycopg2 mentioned in comments
                if "psycopg2" in line.lower() and not any(
                    _normalize(t["name"]) == "postgresql" for t in tools.get("database", [])
                ):
                    _add_tool(tools, "database", "PostgreSQL", "Production database", "optional")
                continue

            pkg = re.split(r"[>=<!;\[#]", line)[0].strip().lower()
            if pkg in PYTHON_MAP:
                cat, desc = PYTHON_MAP[pkg]
                display = DISPLAY_NAMES.get(pkg, pkg)
                _add_tool(tools, cat, display, desc, "pip")

    pp_candidates = [root / "pyproject.toml"] + [
        p for p in root.glob("*/pyproject.toml") if p.parent.name not in EXCLUDED_DIRS
    ]
    for pp in pp_candidates:
        if not pp.exists():
            continue
        # Capture the package name at the start of each quoted string so pinned
        # entries like "spacy>=3.0.0" or "guardrails-ai[extra]>=0.5" also match.
        for pkg in re.findall(r'["\']([A-Za-z0-9][A-Za-z0-9._-]*)', pp.read_text()):
            pkg = pkg.lower()
            if pkg in PYTHON_MAP:
                cat, desc = PYTHON_MAP[pkg]
                display = DISPLAY_NAMES.get(pkg, pkg)
                _add_tool(tools, cat, display, desc, "pip")
    return tools


def scan_node(root: Path) -> dict:
    tools: dict = {}
    # Scan root package.json + one level of subdirectories (monorepos / frontend dirs)
    pj_candidates = [root / "package.json"] + [
        p for p in root.glob("*/package.json") if p.parent.name not in EXCLUDED_DIRS
    ]
    for pj in pj_candidates:
        if not pj.exists():
            continue
        try:
            data = json.loads(pj.read_text())
        except Exception:
            continue
        all_deps: dict = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        for pkg in all_deps:
            key = pkg.lower()
            if key in NODE_MAP:
                cat, desc = NODE_MAP[key]
                badge = "devDep" if pkg in data.get("devDependencies", {}) else "dep"
                _add_tool(tools, cat, pkg, desc, badge)
    return tools


def scan_python_source(root: Path) -> dict:
    """Detect optional/dynamic SDKs by scanning Python source for find_spec() calls and backend enums."""
    tools: dict = {}

    find_spec_re    = re.compile(r'find_spec\(["\'](\w+)["\']')
    import_mod_re   = re.compile(r'import_module\(["\'](\w+)["\']')
    lakera_re       = re.compile(r'lakera\.ai|["\']lakera["\']|LAKERA\s*=')
    ga_guard_re     = re.compile(r'GA_GUARD|["\']ga_guard["\']')
    presidio_anon_re = re.compile(r'presidio_anonymizer|presidio-anonymizer')

    seen_mods: set = set()
    has_lakera     = False
    has_ga_guard   = False
    has_pres_anon  = False

    for py_file in _iter_files(root, "*.py"):
        try:
            content = py_file.read_text(errors="ignore")
        except Exception:
            continue
        for m in find_spec_re.finditer(content):
            seen_mods.add(m.group(1))
        for m in import_mod_re.finditer(content):
            seen_mods.add(m.group(1))
        if lakera_re.search(content):
            has_lakera = True
        if ga_guard_re.search(content):
            has_ga_guard = True
        if presidio_anon_re.search(content):
            has_pres_anon = True

    for mod in seen_mods:
        if mod in FIND_SPEC_MAP:
            cat, name, desc = FIND_SPEC_MAP[mod]
            _add_tool(tools, cat, name, desc, "optional")

    if has_lakera:
        _add_tool(tools, "ai_sdk", "Lakera Guard", "Cloud REST prompt-injection API", "optional")
    if has_ga_guard:
        _add_tool(tools, "ai_sdk", "GA Guard", "Adversarial content detection", "optional")
    if has_pres_anon:
        # Only add if not already captured from commented requirements in any category
        already = any(
            _normalize(t["name"]) == "presidioanonymizer"
            for items in tools.values() for t in items
        )
        if not already:
            _add_tool(tools, "nlp", "Presidio Anonymizer", "PII redaction engine", "optional")

    return tools


def detect_languages(root: Path) -> list:
    langs = []
    seen: set = set()
    checks = [
        ("requirements.txt",  "Python",                  "Primary language"),
        ("pyproject.toml",    "Python",                  "Primary language"),
        ("package.json",      "JavaScript / TypeScript", "Primary language"),
        ("go.mod",            "Go",                      "Primary language"),
        ("Cargo.toml",        "Rust",                    "Primary language"),
        ("pom.xml",           "Java (Maven)",            "Primary language"),
        ("build.gradle",      "Java / Kotlin",           "Primary language"),
        ("composer.json",     "PHP",                     "Primary language"),
        ("Gemfile",           "Ruby",                    "Primary language"),
    ]
    for fname, lang, desc in checks:
        if (root / fname).exists() and lang not in seen:
            seen.add(lang)
            langs.append({"name": lang, "desc": desc, "badge": "lang"})
            if lang == "Python":
                langs.append({"name": "pip / venv", "desc": "Package management", "badge": "lang"})
    if (root / "tsconfig.json").exists() or list(root.glob("src/**/*.ts")):
        if "TypeScript" not in seen:
            langs.append({"name": "TypeScript", "desc": "Type-safe JS", "badge": "lang"})
    return langs


def detect_databases_from_files(root: Path) -> list:
    """Detect database systems from docker-compose, env files, and deployment configs."""
    found: list = []
    seen: set = set()

    def add(name, desc, badge):
        norm = _normalize(name)
        if norm not in seen:
            seen.add(norm)
            found.append({"name": name, "desc": desc, "badge": badge})

    config_files = (
        ["docker-compose.yml", "docker-compose.yaml", ".env", ".env.example", ".env.sample"]
        + [f.name for f in root.glob("*.env")]
    )
    for fname in config_files:
        fpath = root / fname
        if not fpath.exists():
            continue
        try:
            content = fpath.read_text(errors="ignore").lower()
        except Exception:
            continue
        if "sqlite://" in content:
            add("SQLite", "Embedded / dev database", "core")
        if any(x in content for x in ["postgres://", "postgresql://", "image: postgres", "image: postgresql"]):
            add("PostgreSQL", "Production database", "prod")
        if any(x in content for x in ["redis://", "image: redis"]):
            add("Redis", "Cache / distributed rate limiting", "optional")
        if "mongodb://" in content or "image: mongo" in content:
            add("MongoDB", "Document store", "optional")
        if "mysql://" in content or "image: mysql" in content:
            add("MySQL", "Relational database", "optional")

    return found


def detect_infra(root: Path) -> list:
    infra = []
    if (root / "Dockerfile").exists():
        infra.append({"name": "Docker", "desc": "Container image", "badge": "deploy"})
    for name in ["docker-compose.yml", "docker-compose.yaml"]:
        if (root / name).exists():
            infra.append({"name": "Docker Compose", "desc": "Multi-service stack", "badge": "deploy"})
            break
    yamls = [f.name for f in _iter_files(root, "*.yaml")] + [f.name for f in _iter_files(root, "*.yml")]
    if any("k8s" in y or "kubernetes" in y or "deployment" in y for y in yamls):
        infra.append({"name": "Kubernetes", "desc": "Container orchestration", "badge": "prod"})
    if (root / ".github" / "workflows").exists():
        infra.append({"name": "GitHub Actions", "desc": "CI/CD pipeline", "badge": "ci"})
    if (root / ".gitlab-ci.yml").exists():
        infra.append({"name": "GitLab CI", "desc": "CI/CD pipeline", "badge": "ci"})
    if (root / "nginx.conf").exists() or (root / "nginx").is_dir():
        infra.append({"name": "nginx", "desc": "Reverse proxy / TLS", "badge": "prod"})
    if (root / "Caddyfile").exists():
        infra.append({"name": "Caddy", "desc": "Automatic HTTPS proxy", "badge": "prod"})
    if (root / "alembic.ini").exists():
        infra.append({"name": "Alembic Migrations", "desc": "DB schema version control", "badge": "tool"})
    return infra


def collect(root: Path) -> dict:
    tools: dict = {}

    langs = detect_languages(root)
    if langs:
        tools["language"] = langs

    # Requirements / package.json
    for cat, items in scan_python(root).items():
        tools.setdefault(cat, []).extend(items)
    for cat, items in scan_node(root).items():
        tools.setdefault(cat, []).extend(items)

    # Source-based detection (runs after requirements so it can fill gaps)
    for cat, items in scan_python_source(root).items():
        for item in items:
            _add_tool(tools, cat, item["name"], item["desc"], item["badge"])

    # Database systems from deployment config
    db_tools = detect_databases_from_files(root)
    for t in db_tools:
        _add_tool(tools, "database", t["name"], t["desc"], t["badge"])

    # Infra
    infra = detect_infra(root)
    if infra:
        tools.setdefault("infra", []).extend(infra)

    # Final dedup within each category by normalized name
    for cat in tools:
        seen: set = set()
        uniq = []
        for t in tools[cat]:
            key = _normalize(t["name"])
            if key not in seen:
                seen.add(key)
                uniq.append(t)
        tools[cat] = uniq

    return tools


# ── Architecture diagram ──────────────────────────────────────────────────────

def build_arch_html(tools: dict) -> str:
    web_items = [t["name"] for t in tools.get("web", [])[:4]]
    ai_items  = [t["name"] for t in tools.get("ai_sdk", [])[:6]]
    nlp_items = [t["name"] for t in tools.get("nlp", [])[:3]]
    db_items  = [t["name"] for t in tools.get("database", [])[:3]]
    obs_items = [t["name"] for t in tools.get("observability", [])[:2]]
    fe_items  = [t["name"] for t in tools.get("frontend", [])[:2]]
    has_sec   = bool(tools.get("security"))

    S = 'style="font-size:.58rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#334155;text-align:center;padding:2px 0;margin-bottom:6px"'

    def lbl(txt):
        return f'<div {S}>{txt}</div>'

    def arrow():
        return '<div style="color:#1e3a5f;font-size:1.3rem;text-align:center;padding:4px 0;line-height:1">&#8595;</div>'

    rows = []

    # Layer 1 — Consumer
    app_label = "Your LLM Application" if (ai_items or nlp_items) else "Your Application"
    app_sub   = "Chatbot / Agent / RAG Pipeline" if (ai_items or nlp_items) else "Client / Consumer"
    rows.append(lbl("CONSUMER"))
    rows.append(
        '<div class="arch-row">'
        '<div class="arch-box" style="background:#1e1b4b;border-color:#4338ca;color:#a5b4fc;min-width:360px">'
        f'{app_label}'
        f'<div style="font-size:.65rem;opacity:.6;margin-top:4px;font-weight:400">{app_sub}</div>'
        '</div></div>'
    )
    rows.append(arrow())

    # Layer 2 — API / Middleware
    if web_items:
        label = " &nbsp;&middot;&nbsp; ".join(web_items)
        sub_parts: list = []
        if has_sec:
            sub_parts.append("API Key Auth")
        sub_parts += ["Rate Limiting", "CORS Middleware"]
        rows.append(lbl("API / MIDDLEWARE"))
        rows.append(
            '<div class="arch-row">'
            '<div class="arch-box" style="background:#14532d;border-color:#16a34a;color:#86efac;min-width:360px">'
            f'{label}'
            f'<div style="font-size:.65rem;opacity:.6;margin-top:4px;font-weight:400">'
            f'{" &nbsp;&middot;&nbsp; ".join(sub_parts)}</div>'
            '</div></div>'
        )
        rows.append(arrow())

    # Layer 3 — AI Guardrails + NLP
    all_ai = ai_items + nlp_items
    if all_ai:
        chips = "".join(
            f'<span style="background:#162744;border:1px solid rgba(37,99,235,.4);border-radius:6px;'
            f'padding:4px 11px;font-size:.72rem;font-weight:600;color:#93c5fd">{n}</span>'
            for n in all_ai
        )
        rows.append(lbl("AI GUARDRAILS &amp; NLP"))
        rows.append(
            '<div class="arch-row">'
            '<div class="arch-box" style="background:#1a2d4a;border-color:#2563eb;color:#60a5fa;'
            'min-width:360px;max-width:560px;width:100%">'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin-bottom:8px">{chips}</div>'
            '<div style="font-size:.6rem;color:#475569">'
            'Optional &mdash; loaded at runtime via importlib.find_spec()</div>'
            '</div></div>'
        )
        rows.append(arrow())

    # Layer 4 — Data · Observability · Frontend
    bottom: list = []
    if db_items:
        inner = "".join(
            f'<div style="font-size:.72rem;font-weight:500;padding:2px 0">{n}</div>'
            for n in db_items
        )
        bottom.append(
            '<div class="arch-box" style="background:#1c1917;border-color:#78350f;'
            'color:#fbbf24;flex:1;min-width:130px">'
            '<div style="font-size:.58rem;text-transform:uppercase;letter-spacing:.1em;'
            'opacity:.5;margin-bottom:6px">Storage</div>'
            + inner + '</div>'
        )
    if obs_items:
        inner = "".join(
            f'<div style="font-size:.72rem;font-weight:500;padding:2px 0">{n}</div>'
            for n in obs_items
        )
        bottom.append(
            '<div class="arch-box" style="background:#134e4a;border-color:#0d9488;'
            'color:#5eead4;flex:1;min-width:130px">'
            '<div style="font-size:.58rem;text-transform:uppercase;letter-spacing:.1em;'
            'opacity:.5;margin-bottom:6px">Observability</div>'
            + inner + '</div>'
        )
    if fe_items:
        inner = "".join(
            f'<div style="font-size:.72rem;font-weight:500;padding:2px 0">{n}</div>'
            for n in fe_items
        )
        bottom.append(
            '<div class="arch-box" style="background:#1e293b;border-color:#475569;'
            'color:#94a3b8;flex:1;min-width:130px">'
            '<div style="font-size:.58rem;text-transform:uppercase;letter-spacing:.1em;'
            'opacity:.5;margin-bottom:6px">Dashboard</div>'
            + inner + '</div>'
        )
    if bottom:
        rows.append(lbl("DATA &nbsp;&middot;&nbsp; OBSERVABILITY &nbsp;&middot;&nbsp; FRONTEND"))
        rows.append(
            f'<div class="arch-row" style="align-items:stretch;gap:12px">{"".join(bottom)}</div>'
        )

    return "\n    ".join(rows)


# ── Guided tour ────────────────────────────────────────────────────────────────

TOUR_CSS = (
    ".corner-btn{"
    "position:fixed;top:20px;z-index:40;"
    "width:34px;height:34px;border-radius:50%;"
    "background:var(--bg3);border:1px solid var(--border);color:var(--muted);"
    "font-family:var(--sans);font-weight:700;font-size:.85rem;cursor:pointer;"
    "display:flex;align-items:center;justify-content:center;"
    "transition:border-color .2s,color .2s;}"
    "#theme-toggle.corner-btn{right:20px}"
    "#tour-restart.corner-btn{right:64px}"
    ".corner-btn:hover{border-color:var(--green);color:var(--green)}"
    ".tour-overlay{position:fixed;inset:0;z-index:50;background:transparent}"
    ".tour-spot{"
    "position:absolute;z-index:51;border-radius:14px;"
    "box-shadow:0 0 0 9999px rgba(0,0,0,.65);"
    "pointer-events:none;transition:top .35s ease,left .35s ease,"
    "width .35s ease,height .35s ease;}"
    ":root[data-theme=\"light\"] .tour-spot{box-shadow:0 0 0 9999px rgba(15,23,42,.45)}"
    ".tour-card{"
    "position:absolute;z-index:52;width:320px;max-width:calc(100vw - 40px);"
    "background:var(--bg3);border:1px solid var(--border2);border-radius:14px;"
    "padding:20px 22px;box-shadow:0 12px 40px rgba(0,0,0,.5);"
    "font-family:var(--sans);transition:top .35s ease,left .35s ease;}"
    ".tour-step{font-family:var(--mono);font-size:.65rem;color:var(--muted);"
    "text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px}"
    ".tour-title{font-size:.95rem;font-weight:700;color:var(--text);margin-bottom:8px}"
    ".tour-body{font-size:.8rem;color:#94a3b8;line-height:1.55;margin-bottom:16px}"
    ":root[data-theme=\"light\"] .tour-body{color:#475569}"
    ".tour-controls{display:flex;align-items:center;justify-content:space-between;gap:10px}"
    ".tour-skip{"
    "font-size:.72rem;color:var(--muted);background:none;border:none;"
    "cursor:pointer;text-decoration:underline;padding:0;}"
    ".tour-skip:hover{color:#94a3b8}"
    ":root[data-theme=\"light\"] .tour-skip:hover{color:#334155}"
    ".tour-btns{display:flex;gap:8px}"
    ".tour-btn{"
    "font-family:var(--sans);font-size:.75rem;font-weight:600;"
    "padding:7px 14px;border-radius:8px;cursor:pointer;"
    "border:1px solid var(--border2);background:var(--bg4);color:var(--text);"
    "transition:border-color .2s;}"
    ".tour-btn:hover{border-color:var(--green)}"
    ".tour-btn.primary{background:var(--green);border-color:var(--green);color:#052e12}"
    ".tour-close{"
    "position:absolute;top:10px;right:12px;background:none;border:none;"
    "color:var(--muted);font-size:1rem;cursor:pointer;line-height:1;padding:4px;}"
    ".tour-close:hover{color:#94a3b8}"
    ":root[data-theme=\"light\"] .tour-close:hover{color:#334155}"
)

THEME_JS = """
(function(){
  var toggle = document.getElementById('theme-toggle');
  var root = document.documentElement;
  if (toggle) {
    toggle.addEventListener('click', function(){
      var goingLight = root.getAttribute('data-theme') !== 'light';
      root.setAttribute('data-theme', goingLight ? 'light' : 'dark');
      toggle.textContent = goingLight ? '\\ud83c\\udf19' : '\\u2600\\ufe0f';
    });
  }
})();
"""

TOUR_JS = """
(function(){
  var STEPS = [
    {sel:'.stats-wrap', title:'Auto-detected counts', body:'Total tools, categories, and (when present) AI guardrail SDKs and data stores.'},
    {sel:'#section-architecture', title:'System architecture', body:'How the pieces fit together — consumer → API/middleware → AI/NLP → data & observability — built from what was actually detected, not a template.'},
    {sel:'#section-numbers', title:'By the numbers', body:'Category breakdown at a glance, tallest bar first.'},
    {sel:'#section-stack', title:'Full stack', body:'Every detected tool, grouped by category, with a badge showing how it was found (pip install, npm dependency, detected in source, etc.).'},
    {sel:'.legend-wrap', title:'Badge reference', body:'What each badge on a tool card means.'},
    {sel:'#theme-toggle', title:'One more thing', body:'Toggle light and dark mode anytime. That\\'s the tour — click the ? button to see it again.'}
  ];
  var DISMISS_KEY = 'gts_tour_v1_dismissed';
  var overlay, spot, card, active = [], cur = -1;

  function storageGet(){
    try { return localStorage.getItem(DISMISS_KEY) === '1'; } catch (e) { return false; }
  }
  function storageSet(){
    try { localStorage.setItem(DISMISS_KEY, '1'); } catch (e) {}
  }

  function resolveSteps(){
    return STEPS.filter(function(s){
      var el = document.querySelector(s.sel);
      if (!el) return false;
      var r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });
  }

  function buildUI(){
    overlay = document.createElement('div');
    overlay.className = 'tour-overlay';
    spot = document.createElement('div');
    spot.className = 'tour-spot';
    card = document.createElement('div');
    card.className = 'tour-card';
    card.innerHTML =
      '<button class="tour-close" aria-label="Close">\\u00d7</button>' +
      '<div class="tour-step"></div>' +
      '<div class="tour-title"></div>' +
      '<div class="tour-body"></div>' +
      '<div class="tour-controls">' +
        '<button class="tour-skip">Skip tour</button>' +
        '<div class="tour-btns">' +
          '<button class="tour-btn tour-back">Back</button>' +
          '<button class="tour-btn primary tour-next">Next</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(overlay);
    document.body.appendChild(spot);
    document.body.appendChild(card);

    overlay.addEventListener('click', endTour);
    card.querySelector('.tour-close').addEventListener('click', endTour);
    card.querySelector('.tour-skip').addEventListener('click', endTour);
    card.querySelector('.tour-back').addEventListener('click', function(){ go(cur - 1); });
    card.querySelector('.tour-next').addEventListener('click', function(){
      if (cur >= active.length - 1) { endTour(); } else { go(cur + 1); }
    });
    document.addEventListener('keydown', function(e){
      if (overlay.style.display !== 'none' && e.key === 'Escape') endTour();
    });
    window.addEventListener('resize', function(){
      if (cur >= 0 && cur < active.length) position(active[cur].el);
    });
  }

  function position(el){
    var r = el.getBoundingClientRect();
    var pad = 10;
    var top = r.top + window.scrollY - pad;
    var left = r.left + window.scrollX - pad;
    spot.style.top = top + 'px';
    spot.style.left = left + 'px';
    spot.style.width = (r.width + pad * 2) + 'px';
    spot.style.height = (r.height + pad * 2) + 'px';

    var cardTop = top + r.height + pad * 2 + 12;
    var viewportBottom = window.scrollY + window.innerHeight;
    if (cardTop + 200 > viewportBottom) {
      cardTop = Math.max(window.scrollY + 12, top - 12 - 220);
    }
    var cardLeft = Math.min(
      Math.max(left, window.scrollX + 20),
      window.scrollX + window.innerWidth - 340
    );
    card.style.top = cardTop + 'px';
    card.style.left = cardLeft + 'px';
  }

  function go(i){
    if (i < 0 || i >= active.length) return;
    cur = i;
    var step = active[i];
    step.el = document.querySelector(step.sel);
    if (!step.el) { endTour(); return; }
    step.el.scrollIntoView({block: 'center', behavior: 'smooth'});
    card.querySelector('.tour-step').textContent = (i + 1) + ' / ' + active.length;
    card.querySelector('.tour-title').textContent = step.title;
    card.querySelector('.tour-body').textContent = step.body;
    card.querySelector('.tour-back').style.visibility = i === 0 ? 'hidden' : 'visible';
    card.querySelector('.tour-next').textContent = i === active.length - 1 ? 'Done' : 'Next';
    setTimeout(function(){ position(step.el); }, 350);
  }

  function startTour(){
    active = resolveSteps();
    if (!active.length) return;
    if (!overlay) buildUI();
    overlay.style.display = 'block';
    spot.style.display = 'block';
    card.style.display = 'block';
    go(0);
  }

  function endTour(){
    storageSet();
    if (overlay) overlay.style.display = 'none';
    if (spot) spot.style.display = 'none';
    if (card) card.style.display = 'none';
    cur = -1;
  }

  var restartBtn = document.getElementById('tour-restart');
  if (restartBtn) restartBtn.addEventListener('click', startTour);

  if (!storageGet()) {
    setTimeout(startTour, 700);
  }
})();
"""


# ── HTML renderer ─────────────────────────────────────────────────────────────

def render_html(tools: dict, project_name: str) -> str:
    total     = sum(len(v) for v in tools.values())
    cat_count = len(tools)
    max_count = max((len(v) for v in tools.values()), default=1)
    ai_count  = len(tools.get("ai_sdk", []))
    db_count  = len(tools.get("database", []))
    today     = datetime.date.today().strftime("%B %d, %Y")

    arch_html = build_arch_html(tools)

    # ── Bar chart ──
    bars_html = ""
    for cat, items in tools.items():
        if not items:
            continue
        meta = CATEGORY_META.get(cat, CATEGORY_META["other"])
        _, dot_color, _ = COLOR_CSS.get(meta["color"], COLOR_CSS["gray"])
        pct = round(len(items) / max_count * 100)
        bars_html += (
            '<div class="bar-row">'
            f'<div class="bar-lbl"><span class="bar-icon">{meta["icon"]}</span>{meta["label"]}</div>'
            f'<div class="bar-outer"><div class="bar-inner" style="width:{pct}%;background:{dot_color}"></div></div>'
            f'<span class="bar-num" style="color:{dot_color}">{len(items)}</span>'
            '</div>'
        )

    # ── Cards ──
    cards_html = ""
    for cat, items in tools.items():
        if not items:
            continue
        meta = CATEGORY_META.get(cat, CATEGORY_META["other"])
        icon_bg, dot_color, title_color = COLOR_CSS.get(meta["color"], COLOR_CSS["gray"])
        plural = "tools" if len(items) != 1 else "tool"

        tool_rows = ""
        for t in items:
            bg, fg = BADGE_CSS.get(t.get("badge", "tool"), BADGE_CSS["tool"])
            tool_rows += (
                '<div class="tool">'
                f'<span class="dot" style="background:{dot_color}"></span>'
                f'<span class="tool-name">{t["name"]}</span>'
                f'<span class="tool-desc">{t["desc"]}</span>'
                f'<span class="badge" style="background:{bg};color:{fg}">{t.get("badge", "")}</span>'
                '</div>'
            )

        cards_html += (
            f'<div class="card" style="--c:{dot_color};--c-bg:{icon_bg}">'
            '<div class="card-top">'
            f'<span class="card-icon" style="background:{icon_bg}">{meta["icon"]}</span>'
            '<div>'
            f'<div class="card-title" style="color:{title_color}">{meta["label"]}</div>'
            f'<div class="card-sub">{len(items)} {plural}</div>'
            '</div>'
            '</div>'
            f'<div class="tool-list">{tool_rows}</div>'
            '</div>'
        )

    # ── Stat cards ──
    stats_html = (
        '<div class="stat-card">'
        f'<div class="stat-num">{total}</div>'
        '<div class="stat-lbl">Total Tools</div>'
        '</div>'
        '<div class="stat-card">'
        f'<div class="stat-num">{cat_count}</div>'
        '<div class="stat-lbl">Categories</div>'
        '</div>'
    )
    if ai_count:
        stats_html += (
            '<div class="stat-card stat-accent">'
            f'<div class="stat-num">{ai_count}</div>'
            '<div class="stat-lbl">AI Guardrails</div>'
            '</div>'
        )
    if db_count:
        stats_html += (
            '<div class="stat-card">'
            f'<div class="stat-num">{db_count}</div>'
            '<div class="stat-lbl">Data Stores</div>'
            '</div>'
        )

    # CSS as a plain string (no f-string) so CSS braces don't need escaping
    css = (
        "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}"
        ":root{"
        "--bg:#0f172a;--bg2:#111827;--bg3:#161e2e;--bg4:#1a2535;"
        "--border:#1e293b;--border2:#263347;"
        "--text:#f1f5f9;--muted:#64748b;--dim:#334155;"
        "--green:#22c55e;"
        "--mono:'JetBrains Mono',monospace;"
        "--sans:'IBM Plex Sans',system-ui,sans-serif;"
        "}"
        ":root[data-theme=\"light\"]{"
        "--bg:#f8fafc;--bg2:#ffffff;--bg3:#ffffff;--bg4:#f1f5f9;"
        "--border:#e2e8f0;--border2:#cbd5e1;"
        "--text:#0f172a;--muted:#64748b;--dim:#94a3b8;"
        "}"
        ":root[data-theme=\"light\"] body{background-image:"
        "radial-gradient(circle,#cbd5e1 1.4px,transparent 1.4px);background-size:24px 24px}"
        ":root[data-theme=\"light\"] h1{color:#0f172a}"
        ":root[data-theme=\"light\"] .stat-num{color:#0f172a}"
        ":root[data-theme=\"light\"] .tool-name{color:#0f172a}"
        ":root[data-theme=\"light\"] .bar-outer{background:#e2e8f0}"
        ":root[data-theme=\"light\"] .tool:hover{background:rgba(15,23,42,.04)}"
        "html{scroll-behavior:smooth}"
        "body{font-family:var(--sans);background:var(--bg);color:var(--text);"
        "line-height:1.6;-webkit-font-smoothing:antialiased;transition:background .25s,color .25s}"
        ".header{"
        "padding:80px 24px 56px;text-align:center;position:relative;overflow:hidden;"
        "border-bottom:1px solid var(--border);}"
        ".header::before{"
        "content:'';position:absolute;inset:0;"
        "background:radial-gradient(ellipse 90% 60% at 50% -10%,"
        "rgba(34,197,94,.07) 0%,transparent 70%);pointer-events:none;}"
        ".header-badge{"
        "display:inline-flex;align-items:center;gap:7px;"
        "background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.2);"
        "border-radius:999px;padding:5px 14px;margin-bottom:24px;"
        "font-size:.7rem;font-weight:600;letter-spacing:.1em;"
        "text-transform:uppercase;color:#22c55e;}"
        ".badge-dot{"
        "width:6px;height:6px;background:#22c55e;border-radius:50%;"
        "animation:pulse 2s ease-in-out infinite;}"
        "@keyframes pulse{"
        "0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.5)}"
        "50%{box-shadow:0 0 0 5px rgba(34,197,94,0)}}"
        "h1{"
        "font-size:clamp(1.8rem,4.5vw,3rem);font-weight:700;letter-spacing:-.03em;"
        "color:#f8fafc;margin-bottom:10px;line-height:1.15;}"
        ".header-sub{color:var(--muted);font-size:.9rem;font-weight:400}"
        ".stats-wrap{"
        "display:flex;flex-wrap:wrap;justify-content:center;gap:14px;"
        "max-width:820px;margin:0 auto;padding:40px 24px 60px;}"
        ".stat-card{"
        "flex:1;min-width:140px;max-width:190px;"
        "background:var(--bg3);border:1px solid var(--border);"
        "border-radius:14px;padding:20px 16px;text-align:center;"
        "transition:border-color .2s,transform .2s;}"
        ".stat-card:hover{border-color:var(--border2);transform:translateY(-2px)}"
        ".stat-card.stat-accent{background:rgba(34,197,94,.05);border-color:rgba(34,197,94,.25)}"
        ".stat-card.stat-accent .stat-num{color:#22c55e}"
        ".stat-num{font-family:var(--mono);font-size:2.4rem;font-weight:600;"
        "color:#f8fafc;line-height:1}"
        ".stat-lbl{font-size:.65rem;color:var(--muted);text-transform:uppercase;"
        "letter-spacing:.1em;margin-top:6px}"
        ".section{max-width:1200px;margin:0 auto;padding:0 24px 72px}"
        ".sec-hdr{display:flex;align-items:center;gap:14px;margin-bottom:32px}"
        ".sec-title{font-size:.65rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:.15em;color:var(--muted);white-space:nowrap}"
        ".sec-line{flex:1;height:1px;background:var(--border)}"
        ".arch{display:flex;flex-direction:column;align-items:center;gap:0;"
        "max-width:900px;margin:0 auto}"
        ".arch-row{display:flex;align-items:center;justify-content:center;"
        "gap:10px;flex-wrap:wrap}"
        ".arch-box{"
        "border-radius:10px;padding:13px 20px;text-align:center;font-size:.82rem;"
        "font-weight:600;border:1px solid;min-width:120px;"
        "transition:transform .2s,box-shadow .2s;}"
        ".arch-box:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.4)}"
        ".chart-wrap{"
        "background:var(--bg3);border:1px solid var(--border);"
        "border-radius:16px;padding:28px 28px 20px;max-width:720px;margin:0 auto;}"
        ".bar-row{display:flex;align-items:center;gap:14px;margin-bottom:13px}"
        ".bar-row:last-child{margin-bottom:0}"
        ".bar-lbl{display:flex;align-items:center;gap:8px;font-size:.78rem;"
        "color:#94a3b8;width:225px;flex-shrink:0;white-space:nowrap;"
        "overflow:hidden;text-overflow:ellipsis;}"
        ".bar-icon{font-size:.9rem}"
        ".bar-outer{flex:1;height:10px;background:#0a0f1a;border-radius:999px;overflow:hidden}"
        ".bar-inner{height:10px;border-radius:999px;transition:width .6s ease}"
        ".bar-num{font-family:var(--mono);font-size:.75rem;font-weight:600;"
        "width:20px;text-align:right;flex-shrink:0}"
        ".cards-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}"
        ".card{"
        "background:var(--bg3);border:1px solid var(--border);"
        "border-left:3px solid var(--c,#475569);border-radius:14px;"
        "overflow:hidden;transition:border-color .2s,transform .2s,box-shadow .2s;}"
        ".card:hover{"
        "border-color:var(--c,#475569);transform:translateY(-3px);"
        "box-shadow:0 8px 28px rgba(0,0,0,.35);}"
        ".card-top{"
        "display:flex;align-items:center;gap:12px;padding:18px 20px 14px;"
        "border-bottom:1px solid var(--border);}"
        ".card-icon{"
        "width:36px;height:36px;border-radius:9px;display:flex;"
        "align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;}"
        ".card-title{font-size:.72rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:.09em}"
        ".card-sub{font-size:.65rem;color:var(--muted);margin-top:2px}"
        ".tool-list{display:flex;flex-direction:column;gap:1px;padding:8px}"
        ".tool{display:flex;align-items:center;gap:9px;padding:8px 12px;"
        "border-radius:8px;transition:background .15s;}"
        ".tool:hover{background:rgba(255,255,255,.03)}"
        ".dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}"
        ".tool-name{font-family:var(--mono);font-size:.76rem;font-weight:500;"
        "color:#e2e8f0;flex:1;min-width:0}"
        ".tool-desc{font-size:.7rem;color:var(--muted);flex:2;min-width:0}"
        ".badge{font-size:.58rem;font-weight:700;padding:2px 8px;border-radius:999px;"
        "flex-shrink:0;white-space:nowrap;font-family:var(--mono);letter-spacing:.02em;}"
        ".legend-wrap{"
        "background:var(--bg3);border:1px solid var(--border);"
        "border-radius:14px;padding:20px 24px;max-width:800px;margin:0 auto;}"
        ".legend-title{font-size:.62rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:.12em;color:var(--muted);margin-bottom:14px;}"
        ".legend-grid{display:flex;flex-wrap:wrap;gap:10px 24px}"
        ".legend-item{display:flex;align-items:center;gap:8px;font-size:.75rem;color:#94a3b8}"
        "footer{text-align:center;padding:28px 24px 40px;font-size:.68rem;"
        "color:var(--dim);border-top:1px solid var(--border);margin-top:24px;}"
        "@media(max-width:640px){"
        ".bar-lbl{width:140px}"
        ".tool-desc{display:none}"
        ".cards-grid{grid-template-columns:1fr}"
        "h1{font-size:1.8rem}}"
    ) + TOUR_CSS

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{project_name} — Tech Stack</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>

<header class="header">
  <div class="header-badge"><span class="badge-dot"></span>Auto-generated</div>
  <h1>{project_name}</h1>
  <p class="header-sub">Complete Technology Stack &nbsp;&middot;&nbsp; {total} tools across {cat_count} categories &nbsp;&middot;&nbsp; {today}</p>
</header>

<div class="stats-wrap">
  {stats_html}
</div>

<div class="section" id="section-architecture">
  <div class="sec-hdr">
    <span class="sec-title">System Architecture</span>
    <div class="sec-line"></div>
    <span class="sec-title" style="color:#334155">how it fits together</span>
  </div>
  <div class="arch">
    {arch_html}
  </div>
</div>

<div class="section" id="section-numbers">
  <div class="sec-hdr">
    <span class="sec-title">By the Numbers</span>
    <div class="sec-line"></div>
  </div>
  <div class="chart-wrap">
    {bars_html}
  </div>
</div>

<div class="section" id="section-stack">
  <div class="sec-hdr">
    <span class="sec-title">Full Stack</span>
    <div class="sec-line"></div>
    <span class="sec-title" style="color:#334155">{total} tools detected</span>
  </div>
  <div class="cards-grid">
    {cards_html}
  </div>
</div>

<div class="section">
  <div class="legend-wrap">
    <div class="legend-title">Badge Reference</div>
    <div class="legend-grid">
      <div class="legend-item"><span class="badge" style="background:#1e293b;color:#94a3b8">pip</span>Installed via requirements.txt</div>
      <div class="legend-item"><span class="badge" style="background:#1e293b;color:#64748b">optional</span>Detected in source (install separately)</div>
      <div class="legend-item"><span class="badge" style="background:#14532d;color:#86efac">dep</span>npm dependency</div>
      <div class="legend-item"><span class="badge" style="background:#1e1b4b;color:#a5b4fc">devDep</span>npm dev dependency</div>
      <div class="legend-item"><span class="badge" style="background:#14532d;color:#86efac">core</span>Always present (embedded)</div>
      <div class="legend-item"><span class="badge" style="background:#431407;color:#fdba74">lang</span>Language / runtime</div>
      <div class="legend-item"><span class="badge" style="background:#3b1f0f;color:#fdba74">deploy</span>Deployment artifact</div>
      <div class="legend-item"><span class="badge" style="background:#1e1b4b;color:#a5b4fc">ci</span>CI/CD integration</div>
    </div>
  </div>
</div>

<footer>
  {project_name} &nbsp;&middot;&nbsp; {total} tools in {cat_count} categories &nbsp;&middot;&nbsp; {today} &nbsp;&middot;&nbsp; generate-tech-stack
</footer>

<button id="theme-toggle" class="corner-btn" aria-label="Toggle light/dark theme" title="Toggle theme">&#9728;&#65039;</button>
<button id="tour-restart" class="corner-btn" title="Take the guided tour">?</button>

<script>{THEME_JS}</script>
<script>{TOUR_JS}</script>
</body>
</html>"""


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root   = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "TECH_STACK.html"

    project_name = root.resolve().name.replace("-", " ").replace("_", " ").title()
    tools = collect(root)

    if not tools:
        print("No recognizable dependency files found.", file=sys.stderr)
        sys.exit(1)

    output.write_text(render_html(tools, project_name))

    total = sum(len(v) for v in tools.values())
    print(f"Written: {output}")
    print(f"Detected {total} tools in {len(tools)} categories")
    for cat, items in tools.items():
        meta = CATEGORY_META.get(cat, CATEGORY_META["other"])
        print(f"  {meta['icon']} {meta['label']}: {', '.join(t['name'] for t in items)}")


if __name__ == "__main__":
    main()
