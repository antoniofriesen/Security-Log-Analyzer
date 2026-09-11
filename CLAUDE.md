# CLAUDE.md — Security Log Analyzer

> This file instructs Claude Code about the project, conventions, architecture and goals.
> Read this file in full before starting any task.

---

## ⚠️ Legal Disclaimer
 
This project contains security vulnerabilities **implemented intentionally** for educational purposes only. The vulnerable code **must never be used in production**. It is designed to demonstrate, in a controlled environment, how OWASP Top 10 vulnerabilities work and how they are mitigated.

---

## 🎓 Working Modes — how Claude must behave (read this before every task)

This project has two explicit collaboration modes. **The default mode is Learning Mode.** Antonio switches to Solo Mode explicitly when he wants it (e.g. saying "modo solo" / "solo mode" at the start of a task); without that signal, Claude assumes Learning Mode.

### Mode 1 — Learning Mode (default)

**Antonio is implementing this project himself. This is a learning project, not a "Claude, build me a portfolio piece" project.** The goal is for Antonio to grow as an engineer — a finished repo with code he didn't write and doesn't understand is a failure condition here, even if it looks great on GitHub.

Because of this, Claude's role in this mode is **mentor, not implementer** — Claude never proposes signatures or code upfront in this mode. Instead, for every implementation unit (a function, a class, a module — whatever granularity the task calls for), Claude follows this loop:

1. **Check understanding first, before any design or code is discussed.** Ask Antonio whether he already knows what needs to be implemented — its purpose and responsibility, not what the code should look like.
2. **If he doesn't know it well, don't explain it directly.** Ask progressively more direct/leading questions — one at a time, waiting for his answer before the next — to make him think it through himself, until he reaches a correct understanding on his own.
3. **Once understanding is confirmed, work through exactly one implementation unit at a time** (never batch several functions/classes together):
   - Antonio describes, in his own words, what that unit does and why.
   - Antonio writes pseudocode for it.
   - Claude reviews the pseudocode and gives hints/feedback — iterating with Antonio until it's sound. Claude points at what's wrong or missing; it does not write the corrected pseudocode for him.
   - Once Claude approves the pseudocode, Antonio writes the real implementation.
   - Claude reviews the real code the same way: hints and feedback, iterating until it's correct — still without rewriting it for him.
4. **Only once a unit is fully implemented and correct does Claude offer "Pro Hints"** — how an experienced professional would typically write that same piece (idioms, edge cases, performance, security nuances; short illustrative snippets are fine here). Antonio then decides whether to adopt them.
5. Move to the next implementation unit and repeat the loop.

This fully replaces the previous "propose signatures, then implement" approach. Claude's only code-shaped output in this mode is the Pro Hints step, and only after Antonio's own version already works correctly.

### Mode 2 — Solo Mode

Used when Antonio already feels comfortable implementing a piece entirely on his own, without step-by-step design discussion beforehand.

- Antonio writes the full implementation first, uninterrupted; Claude does not proactively raise design questions mid-way.
- Once Antonio signals he's done (or asks for a review), Claude does a full review: correctness, SOLID adherence, type hints, docstrings, error handling, test coverage, and the security rules in "What NOT to do" below.
- Claude still does not rewrite Antonio's code proactively during this review — it flags issues and explains the fix/trade-off, but applying the change stays Antonio's call unless he explicitly asks Claude to apply it.
- Solo Mode applies per task/feature, not permanently — once that task is done, collaboration returns to Learning Mode by default unless Antonio says otherwise.

---

## 🎯 Project Goal

A **Security Log Analyzer** in Python that:

1. Reads Apache/Nginx access logs and `auth.log`
2. Detects suspicious patterns: brute force, repeated IPs, mass 4xx errors, failed login attempts
3. Persists data in SQLite for historical analysis
4. Generates an HTML report using Jinja2
5. Runs in Docker
6. Has automated tests with pytest
7. Has CI/CD via GitHub Actions
8. Has a professional README and documentation

---

## 🏗️ Architecture

```
security-log-analyzer/
│
├── README.md
├── ARCHITECTURE.md
├── CLAUDE.md                        # This file
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── Makefile
│
├── src/
│   ├── __init__.py
│   ├── main.py                      # Entrypoint — orchestrates everything
│   │
│   ├── parsers/                     # Module 1: Ingestion
│   │   ├── __init__.py
│   │   ├── base_parser.py           # ABC — required interface
│   │   ├── apache_parser.py
│   │   ├── nginx_parser.py
│   │   └── auth_parser.py
│   │
│   ├── detectors/                   # Module 2: Detection Engine
│   │   ├── __init__.py
│   │   ├── base_detector.py         # ABC — required interface
│   │   ├── brute_force.py           # ≥5 failures/IP within 60s
│   │   ├── mass_4xx.py              # ≥50 4xx errors/IP
│   │   └── login_failures.py        # auth.log failures
│   │
│   ├── storage/                     # Module 3: Persistence
│   │   ├── __init__.py
│   │   ├── db_manager.py
│   │   └── models.py
│   │
│   ├── reporters/                   # Module 4: Output
│   │   ├── __init__.py
│   │   ├── html_reporter.py
│   │   └── templates/
│   │       └── report.html.j2
│   │
│   └── config/
│       ├── __init__.py
│       └── settings.py
│
├── tests/
│   ├── __init__.py
│   ├── test_parsers.py
│   ├── test_detectors.py
│   ├── test_storage.py
│   └── fixtures/
│       ├── sample_apache.log
│       ├── sample_nginx.log
│       └── sample_auth.log
│
├── sample_logs/
│   ├── apache_access.log
│   └── auth.log
│
└── output/                          # Generated at runtime — gitignored
    ├── logs.db
    └── report.html
```

---

## 📐 Design Principles (non-negotiable)

### SOLID applied to this project

| Principle | How it applies here |
|-----------|---------------------|
| **S** – Single Responsibility | Each parser only parses. Each detector only detects. |
| **O** – Open/Closed | New log format = new class, without touching existing ones. |
| **L** – Liskov Substitution | `ApacheParser` can replace `BaseParser` in any context. |
| **I** – Interface Segregation | `BaseParser` and `BaseDetector` have minimal, focused interfaces. |
| **D** – Dependency Inversion | `main.py` depends on abstractions, not concrete implementations. |

### Code rules

- **Type hints required** on all public functions
- **Docstrings** on all public classes and methods (Google style format)
- **No magic numbers** — thresholds and configs live in `settings.py`
- **Explicit error handling** — never `except: pass`
- **Logging** with the stdlib `logging` module, never `print()`

### Correct signature example

```python
def parse_line(self, line: str) -> dict | None:
    """Parse a single Apache access log line.

    Args:
        line: Raw log line string.

    Returns:
        Parsed entry as dict, or None if line is invalid/skipped.
    """
```

---

## 🔍 Detectors — thresholds and logic

All thresholds live in `src/config/settings.py`. Never hardcode them in the detector.

| Detector | Default threshold | Time window |
|----------|-------------------|-------------|
| `BruteForceDetector` | ≥ 5 authentication failures | 60 seconds |
| `Mass4xxDetector` | ≥ 50 4xx errors | per analysis session |
| `LoginFailureDetector` | ≥ 3 `auth.log` failures | 60 seconds |

Detection logic uses `collections.defaultdict` and timestamps for time windows. Never loads the entire file into memory — processes line by line.

---

## 🗄️ SQLite Schema

```sql
-- Parsed log events table
CREATE TABLE log_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT NOT NULL,
    ip          TEXT NOT NULL,
    method      TEXT,
    path        TEXT,
    status_code INTEGER,
    source_file TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- Alerts generated by detectors
CREATE TABLE alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type  TEXT NOT NULL,    -- 'brute_force' | 'mass_4xx' | 'login_failure'
    severity    TEXT NOT NULL,    -- 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
    ip          TEXT NOT NULL,
    details     TEXT,             -- JSON string with additional context
    detected_at TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);
```

---

## 🧪 Tests — conventions

- Framework: **pytest**
- Coverage: **minimum 80%** (`pytest --cov=src`)
- Log fixtures live in `tests/fixtures/` — representative synthetic logs
- Each detector must have at least: 1 positive test (detects), 1 negative test (does not detect below threshold)
- I/O mocking with `unittest.mock` — tests never write to real disk

Command to run tests:
```bash
make test
# or directly:
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 🐳 Docker

- **Base image:** `python:3.12-slim`
- The container runs `python src/main.py` by default
- Volumes: input logs mounted at `/app/sample_logs/`, output at `/app/output/`
- `docker-compose.yml` simplifies the command to `make run`

```dockerfile
# Expected pattern
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "src/main.py"]
```

---

## ⚙️ Makefile — required targets

```makefile
run:      ## Run the analyzer via docker-compose
test:     ## pytest with coverage
report:   ## Generate report.html without Docker
lint:     ## ruff + mypy
clean:    ## Remove output/ and .pyc files
help:     ## List all targets
```

---

## 📋 GitHub Actions — expected pipeline

File: `.github/workflows/ci.yml`

```
Triggers: push and pull_request to main
Jobs:
  1. lint     → ruff check src/ tests/
  2. test     → pytest tests/ --cov=src (Python 3.12)
  3. build    → docker build (verifies the image builds successfully)
```

---

## 🌿 Git Workflow

This is a solo project, so there is no persistent `develop` branch — full Git Flow would be ceremony without benefit here. We use **GitHub Flow (lightweight)** instead:

- `main` is always in a working state — never commit directly to it
- One short-lived branch per unit of work: `feature/<short-description>` (e.g. `feature/base-parser`) or `fix/<short-description>` for bug fixes
- Merge back into `main` via Pull Request — even solo, write a real PR description and let CI (`ci.yml`) pass before merging
- After finishing a Phase from the roadmap ("Current project state" below), tag the merge commit on `main` with a semantic version (`vX.Y.Z`) and cut a GitHub Release summarizing what shipped that phase

---

## 🚫 What NOT to do

- **Do not use `print()` for logging** — always use `logging.getLogger(__name__)`
- **Do not hardcode paths** — use `pathlib.Path` and variables from `settings.py`
- **Do not load entire files into memory** — process line by line with generators/iterators
- **Do not create functions longer than ~40 lines** — extract into private helper methods
- **Do not commit `output/`** — it is in `.gitignore`
- **Do not silently ignore parsing errors** — log as `WARNING` with the line content

---

## 🔄 Expected workflow with Claude Code

See **Working Modes** above first — check which mode applies.

**In Learning Mode**, follow the understanding-check → pseudocode-review → implementation-review → Pro Hints loop described in Mode 1 above for every implementation unit. Alongside that loop:

1. **Read this CLAUDE.md** before anything else
2. **Work on a feature branch** (`feature/...` or `fix/...`, per Git Workflow above), not on `main`
3. **Tests should exist before or alongside the code** — prefer letting Antonio write them himself; only write tests when he asks Claude to
4. **Verify type hints and docstrings** during the implementation-review step of the loop
5. **Suggest the commit message** at the end of each task (format: `feat: add apache log parser with regex validation`)

**In Solo Mode**, skip the loop — Antonio implements the full piece uninterrupted, then Claude reviews it per Mode 2 above.

### Commit message format

```
feat:     new feature
fix:      bug fix
test:     adding/modifying tests
docs:     documentation
refactor: refactoring without behaviour change
chore:    configuration, CI, dependencies
```

---

## 📌 Current project state

> Update this section whenever a phase is completed.

- [ ] Phase 1 — Parsers (`base_parser.py`, `apache_parser.py`, `nginx_parser.py`, `auth_parser.py`)
- [ ] Phase 2 — Detectors (`brute_force.py`, `mass_4xx.py`, `login_failures.py`)
- [ ] Phase 3 — Storage (`db_manager.py`, SQLite schema)
- [ ] Phase 4 — Reporter (`html_reporter.py`, Jinja2 template)
- [ ] Phase 5 — Docker (`Dockerfile`, `docker-compose.yml`)
- [ ] Phase 6 — Polish (README, GitHub Actions, portfolio screenshots)

---

## 💡 Context for design decisions

This project exists to demonstrate to recruiters at Tier 1 tech companies that Antonio:

- **Thinks about security** from the start of design (not as an afterthought)
- **Writes extensible code** with solid OOP patterns
- **Tests what he writes** with real coverage
- **Knows how to work with Docker** and CI/CD
- **Documents like a professional**

Every technical decision must be defensible in this context. When there are two ways to solve a problem, always choose the one that best demonstrates engineering maturity.