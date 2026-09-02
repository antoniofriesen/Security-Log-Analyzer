# Security Log Analyzer

A Python tool that parses Apache/Nginx access logs and `auth.log`, detects suspicious patterns (brute force, mass 4xx errors, repeated failed logins), persists findings in SQLite, and generates an HTML report — built as a hands-on OWASP Top 10 learning project.

---

## ⚠️ Disclaimer

This project contains security vulnerabilities **implemented intentionally**, for educational purposes only. The vulnerable code **must never be used in production**. It exists to demonstrate, in a controlled environment, how OWASP Top 10 vulnerabilities work and how they are mitigated.

---

## Status

- [ ] Phase 1 — Parsers (Apache, Nginx, auth.log)
- [ ] Phase 2 — Detection engine (brute force, mass 4xx, login failures)
- [ ] Phase 3 — SQLite storage
- [ ] Phase 4 — HTML report (Jinja2)
- [ ] Phase 5 — Docker
- [ ] Phase 6 — CI/CD, docs, polish

---

## Installation

_Coming once Phase 5 (Docker) is complete._

## Usage

_Coming once the core pipeline (Phases 1–4) is complete._

## Architecture

_Coming once the module structure exists — see `ARCHITECTURE.md`._

## Testing

_Coming once Phase 1 introduces the first test suite._
