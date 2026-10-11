The **Git Commit Message Generator** is an automated developer utility that bridges code changes and semantic versioning standards.

![Summary](https://github.com/user-attachments/assets/fc2fc6e4-cde2-4e65-96f3-a1447a664475 "Note: Ignore vepython, it's just an alias.")

Instead of manually trying to summarize a messy git diff into a concise, standards-compliant commit message, this tool inspects your staged changes (`git diff --staged`), sends them to **Gemini 2.5 Flash**, and instantly drafts a precise **Conventional Commit** message complete with semantic types (like `feat`, `fix`, `refactor`), appropriate scopes, breaking-change flags, and detailed bodies.

---

### Breakdown of Each File

The project consists of three core components:

#### 1. `schemas.py` (The Data Contract & Output Schema)

This file uses **Pydantic V2** to define the strict data structure (`CommitMessageResponse`) enforced on the Gemini API response, ensuring reliable, typed JSON parsing every time.

* **Fields Captured:** `commit_type`, `scope`, `subject`, `body`, `breaking_change`, and the fully assembled `full_commit_message`.

---

#### 2. `commit_gen.py` (The Core CLI Execution Engine)

This script manages git subprocess execution, API communication, error handling, and terminal rendering.

* **Git Subprocess Automation:** Automatically executes `git diff --staged` under the hood to capture your current work-in-progress changes (with an optional `--file` override for testing with static diffs).
* **Gemini API Integration:** Submits the diff text to `gemini-2.5-flash` with a senior release manager system prompt and strict JSON schema enforcement.
* **Stderr Suppression:** Temporarily redirects `sys.stderr` to eliminate background SDK warning logs during generation.
* **Rich Terminal UI:** Uses Python's `rich` library to render a clean metadata dashboard, syntax-highlighted commit message previews, and quick-copy CLI command helpers.

---

#### 3. `requirements.txt` (Project Dependencies)

Contains the common dependency stack used across your developer tooling suite:

* `google-genai` (Official Google GenAI SDK for Gemini 2.5 Flash)
* `pydantic` (Data validation and schema enforcement)
* `typer` (CLI argument and flag routing)
* `rich` (Terminal styling, panels, tables, and code syntax highlighting)
