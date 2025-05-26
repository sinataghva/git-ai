#!/usr/bin/env python3
"""
Prepare-commit-msg hook for AI-powered commit messages.

Usage:
  • Copy **gitcommit_hook.py** to your repository’s hooks folder:
      `.git/hooks/prepare-commit-msg`  
    and make it executable:
      `chmod +x .git/hooks/prepare-commit-msg`

  • Or install globally:
      ```bash
      mkdir -p ~/.githooks
      cp gitcommit_hook.py ~/.githooks/prepare-commit-msg
      chmod +x ~/.githooks/prepare-commit-msg
      git config --global core.hooksPath ~/.githooks
      ```

Configuration:
  • Ensure your OPENAI_API_KEY is set in the environment (e.g., exported in your shell).

This hook only runs on a fresh 'git commit' (no -m, -t, merge, squash).
If you supply -m/--message or use --no-verify, the hook is skipped.
"""
import os
import sys
import subprocess
from openai import OpenAI

# === Environment Check ===
# Ensure the OpenAI API key is available before proceeding
if not os.environ.get("OPENAI_API_KEY"):
    sys.stderr.write(
        "Error: OPENAI_API_KEY environment variable is not set. \
"        "Please export it in your shell before committing.\n"
    )
    sys.exit(1)

# === Configuration ===
MAX_DIFF_LINES = 1000
MODEL = "gpt-4o"

# === Helpers ===

def get_staged_diff():
    try:
        return subprocess.check_output(["git", "diff", "--cached"], text=True)
    except subprocess.CalledProcessError:
        return ""


def summarize_diff(diff):
    files = {
        line.split()[2][2:]
        for line in diff.splitlines()
        if line.startswith("diff --git")
    }
    header = f"<Large diff: {len(diff.splitlines())} lines>  Changed files:"
    bullets = "\n".join(f"- {f}" for f in sorted(files))
    return f"{header}\n{bullets}"


def generate_commit_message(diff):
    if diff.count("\n") > MAX_DIFF_LINES:
        diff = summarize_diff(diff)

    client = OpenAI()
    system_msg = (
        "You are a commit-message assistant.\n"
        "- First line: concise subject in the imperative mood.\n"
        "- Blank line.\n"
        "- Multi-line description or bullet list of key changes.\n"
        "- Use Conventional Commits format: <type>(<scope>): <subject>.\n"
    )
    user_msg = "Staged changes:\n" + diff

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",  "content": system_msg},
            {"role": "user",    "content": user_msg},
        ],
        temperature=0.2,
        max_tokens=512,
    )
    return resp.choices[0].message.content.strip().strip('"')

# === Hook logic ===
msg_file    = sys.argv[1]
commit_type = sys.argv[2] if len(sys.argv) > 2 else ""

# Only run on a fresh commit (no -m/-t/merge/squash, etc.)
if commit_type == "":
    # Read the existing commit message file
    raw = open(msg_file, "r").read().splitlines()
    # Remove Git comments ('#') and blank lines
    content_lines = [line for line in raw if line.strip() and not line.startswith('#')]
    # If buffer has no user content, generate AI message
    if not content_lines:
        diff   = get_staged_diff()
        ai_msg = generate_commit_message(diff)
        # Write AI draft plus blank lines for editor
        with open(msg_file, "w") as f:
            f.write(ai_msg + "\n\n")

# Exit zero to allow Git to continue
sys.exit(0)
