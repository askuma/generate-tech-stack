/**
 * generate-tech-stack — GitHub Copilot Extension
 *
 * Responds to: @generate-tech-stack /generate-tech-stack [path]
 *
 * Deploy this as a GitHub App with Copilot Extensions enabled.
 * Set the callback URL to: https://<your-host>/agent
 *
 * Install guide: see ../INSTALL.md → GitHub Copilot section
 */

const express  = require("express");
const { execSync } = require("child_process");
const path     = require("path");
const fs       = require("fs");

const app  = express();
app.use(express.json());

const PORT           = process.env.PORT || 3000;
const SKILL_ROOT     = path.join(__dirname, "..");
const ANALYZE_SCRIPT = path.join(SKILL_ROOT, "scripts", "analyze.py");

// ── Run the Python analyzer ───────────────────────────────────────────────────

function runAnalyzer(projectDir, outputFile) {
  const cmd = `python3 "${ANALYZE_SCRIPT}" "${projectDir}" "${outputFile}"`;
  try {
    const out = execSync(cmd, { timeout: 30_000 }).toString().trim();
    return { ok: true, output: out };
  } catch (err) {
    return { ok: false, output: err.message };
  }
}

function quickScan(projectDir) {
  const manifests = ["requirements.txt", "package.json", "go.mod", "Cargo.toml", "pyproject.toml"];
  const found     = manifests.filter((f) => fs.existsSync(path.join(projectDir, f)));
  const tools     = {};

  const pj = path.join(projectDir, "package.json");
  if (fs.existsSync(pj)) {
    try {
      const data = JSON.parse(fs.readFileSync(pj, "utf8"));
      tools["Node.js deps"] = Object.keys({ ...data.dependencies, ...data.devDependencies }).slice(0, 20);
    } catch (_) {}
  }

  const req = path.join(projectDir, "requirements.txt");
  if (fs.existsSync(req)) {
    tools["Python deps"] = fs.readFileSync(req, "utf8")
      .split("\n")
      .filter((l) => l.trim() && !l.startsWith("#"))
      .map((l) => l.split(/[>=<!]/)[0].trim())
      .slice(0, 20);
  }

  return { found, tools };
}

// ── SSE helpers ───────────────────────────────────────────────────────────────

function sse(res, event, data) {
  res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
}

function copilotMsg(res, text) {
  sse(res, "copilot_message", { role: "assistant", content: [{ type: "text", text }] });
}

// ── /agent endpoint ───────────────────────────────────────────────────────────

app.post("/agent", (req, res) => {
  res.setHeader("Content-Type",  "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection",    "keep-alive");

  const lastMsg    = (req.body?.messages ?? []).at(-1)?.content ?? "";
  const match      = lastMsg.match(/generate[-_]tech[-_]stack\s*(\/\S+)?/i);
  const projectDir = match?.[1] || process.cwd();
  const outputFile = path.join(projectDir, "TECH_STACK.html");

  copilotMsg(res, `Scanning \`${projectDir}\` for technologies…`);

  if (fs.existsSync(ANALYZE_SCRIPT)) {
    const result = runAnalyzer(projectDir, outputFile);
    copilotMsg(
      res,
      result.ok
        ? `Tech stack generated!\n\n\`\`\`\n${result.output}\n\`\`\`\n\n📄 Open \`${outputFile}\` in your browser.`
        : `Analysis failed:\n\`\`\`\n${result.output}\n\`\`\``
    );
  } else {
    const { found, tools } = quickScan(projectDir);
    let reply = `**Tech stack detected in \`${projectDir}\`**\n\nManifest files: ${found.join(", ") || "none"}\n\n`;
    for (const [cat, items] of Object.entries(tools)) {
      reply += `**${cat}:** ${items.join(", ")}\n`;
    }
    reply += "\n> Install the full skill to generate the visual HTML report.";
    copilotMsg(res, reply);
  }

  sse(res, "done", {});
  res.end();
});

// ── Health & webhook ──────────────────────────────────────────────────────────

app.get("/health",   (_req, res) => res.json({ status: "ok", skill: "generate-tech-stack" }));
app.post("/webhook", (_req, res) => res.status(200).send("ok"));

app.listen(PORT, () => {
  console.log(`generate-tech-stack Copilot Extension  →  http://localhost:${PORT}`);
  console.log(`Agent endpoint: POST http://localhost:${PORT}/agent`);
});
