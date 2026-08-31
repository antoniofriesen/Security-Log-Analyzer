# CLAUDE.md — Security Log Analyzer

> This file instructs Claude Code about the project, conventions, architecture and goals.
> Read this file in full before starting any task.

---

## ⚠️ Legal Disclaimer
 
This project contains security vulnerabilities **implemented intentionally** for educational purposes only. The vulnerable code **must never be used in production**. It is designed to demonstrate, in a controlled environment, how OWASP Top 10 vulnerabilities work and how they are mitigated.

---

## 👤 Developer Context

- **Name:** Antonio
- **Location:** Hamburg, Germany
- **Current training:** Ausbildung Fachinformatiker Anwendungsentwicklung at AXRO GmbH (Hamburg) — expected completion July 2028

### Current stack and knowledge
- **Languages:** PHP/Laravel, Python (PCEP certified), MySQL, Git
- **Infrastructure:** Basic Docker, REST APIs, Basic CI/CD
- **Security:** XSS, CSRF, SQL Injection, OWASP awareness
- **In progress:** CCNA v7, Junior Cybersecurity Analyst path (Cisco NetAcad)

### Career trajectory — the most important context

Antonio has a structured career plan across three horizons:

**Horizon 1 — next 12–18 months (immediate):**
Transition to a **Junior Softwareentwickler** position at a Tier 1 company in Hamburg before the end of the Ausbildung. Target companies: Otto Tech, Airbus, Dataport, About You, New Work SE. Minimum target salary: €42,000. AXRO is a B2B office supplies company — it is not a tech company and does not offer a cybersecurity growth path. The early transition is a conscious strategic decision.

**Horizon 2 — 2 to 4 years:**
Within the Tier 1 company, grow laterally into a **Security Engineer / DevSecOps** role, combining the development background with progressive specialisation in offensive and defensive security.

**Horizon 3 — long term:**
**Lead AI Security Architect** — responsible for designing secure systems with AI components, defining security policies and leading technical teams at the intersection of AI, cloud and security.

### What this means for this project

This project is not an academic exercise. It is a portfolio piece that needs to communicate to recruiters at target companies that Antonio:
- Thinks like a senior software engineer (design patterns, SOLID, testability)
- Already has a security mindset integrated into development (not as an afterthought)
- Knows how to work with professional tools (Docker, CI/CD, GitHub Actions)
- Documents and communicates like a professional

Every technical decision must be defensible in this context. When there are two ways to solve a problem, always choose the one that best demonstrates engineering maturity.

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

## 🚫 What NOT to do

- **Do not use `print()` for logging** — always use `logging.getLogger(__name__)`
- **Do not hardcode paths** — use `pathlib.Path` and variables from `settings.py`
- **Do not load entire files into memory** — process line by line with generators/iterators
- **Do not create functions longer than ~40 lines** — extract into private helper methods
- **Do not commit `output/`** — it is in `.gitignore`
- **Do not silently ignore parsing errors** — log as `WARNING` with the line content

---

## 🔄 Expected workflow with Claude Code

When Antonio asks to implement a feature or file:

1. **Read this CLAUDE.md** before anything else
2. **Propose class/function signatures** before writing the full implementation
3. **Write tests before or alongside the code** (never after)
4. **Verify type hints and docstrings** before considering a task complete
5. **Suggest the commit message** at the end of each task (format: `feat: add apache log parser with regex validation`)

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

This project exists to demonstrate to recruiters at Tier 1 companies (Otto Tech, Airbus, Dataport, About You, New Work SE) that Antonio:

- **Thinks about security** from the start of design (not as an afterthought)
- **Writes extensible code** with solid OOP patterns
- **Tests what he writes** with real coverage
- **Knows how to work with Docker** and CI/CD
- **Documents like a professional**

Every technical decision must be defensible in this context. When there are two ways to solve a problem, always choose the one that best demonstrates engineering maturity.