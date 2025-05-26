# Git Automation Scripts

This repository contains Python scripts to automate Git workflows using the OpenAI API:

* **`gitlog.py`**: Generate human-readable release notes.
* **`gitcommit.py`** (now via **`gitcommit_hook.py`**): Automatically draft commit messages.

## Disclaimer

These scripts are provided as a proof of concept. There is no guarantee they will work exactly as intended. Users are responsible for any consequences of sending code diffs or commit messages to the OpenAI API. Use at your own risk, and ensure you comply with your organization’s AI and security policies.

## Scripts Overview

### `gitlog.py`

Generates a non-technical, human-readable summary of Git commits for release notes.

#### Features

* Fetch commits by date, range, author, or grep pattern.
* Produce clear summaries for non-technical audiences.
* Optional technical summaries.

#### Usage

```sh
python gitlog.py [--since-date YYYY-MM-DD] [--range A..B] [--author "Name"] [--grep "pattern"] [--technical]
```

### `gitcommit.py` (Legacy CLI)

Stages changes, uses OpenAI to draft a commit message, and lets you:

1. **Accept** the generated message.
2. **Edit** it in your editor.
3. **Abort**, unstaging all changes.

#### Usage

```sh
python gitcommit.py
```

---

### `gitcommit_hook.py` (Prepare-commit-msg Hook)

A single-file Git hook that auto-fills your commit message buffer using AI when you run `git commit` without `-m`.

#### Installation

##### Per-repo

1. Copy this file to your repo’s hooks folder:

   ```sh
   cp gitcommit_hook.py .git/hooks/prepare-commit-msg
   chmod +x .git/hooks/prepare-commit-msg
   ```

2. Run in your repo as usual:

   ```sh
   git add .
   git commit
   ```

   Your editor will open with an AI-generated draft.

##### Global

1. Create a global hooks directory:

   ```sh
   mkdir -p ~/.githooks
   cp gitcommit_hook.py ~/.githooks/prepare-commit-msg
   chmod +x ~/.githooks/prepare-commit-msg
   git config --global core.hooksPath ~/.githooks
   ```

2. Use `git commit` anywhere without `-m`:

   ```sh
   git add .
   git commit
   ```

> **Note:** The hook only runs when no commit message is provided (no `-m`, `-t`, merge, or squash). To skip it, use `git commit -m "msg"` or `--no-verify`.

## Prerequisites

* Python 3.7+
* OpenAI Python client: `pip install openai`

### Environment

Set your OpenAI API key in your shell:

```sh
export OPENAI_API_KEY="sk-..."
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT License](LICENSE)
