import os
import sys
import subprocess
import tempfile
import click
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI()

# Constants for diff handling
MAX_DIFF_LINES = 1000


def get_staged_diff():
    """
    Returns the staged diff as a string, or None on error.
    """
    try:
        diff = subprocess.check_output(["git", "diff", "--cached"], text=True)
        return diff
    except subprocess.CalledProcessError:
        return None


def summarize_diff(diff):
    """
    For large diffs, return a file-level summary and warn the user.

    This function:
    1. Parses the diff output line by line, looking for 'diff --git' markers.
    2. Extracts the file path for each changed file.
    3. Builds a bullet list of unique, sorted file paths.
    4. Returns a summary string indicating how many lines the diff had,
       followed by the list of changed files.
    """
    files = set()  # Collect unique file paths
    for line in diff.splitlines():
        # Identify lines that mark the start of changes for a file
        if line.startswith("diff --git"):
            parts = line.split()
            # The third part is of the form 'a/<path>'
            if len(parts) >= 3:
                path = parts[2][2:]  # Remove 'a/' prefix
                files.add(path)
    # Create a sorted, bullet-point list of file paths
    summary = "\n".join(f"- {file}" for file in sorted(files))
    # Prepend a header with total line count and the file list
    header = f"<Large diff detected ({len(diff.splitlines())} lines)>\nFile changes:"  
    return f"{header}\n{summary}"


def generate_commit_message(diff):
    """
    Ask GPT to generate a commit message based on the diff.
    """
    # Switch to compact mode if diff too large
    prompt_diff = diff
    if diff.count('\n') > MAX_DIFF_LINES:
        prompt_diff = summarize_diff(diff)
        click.secho("\n[Warning] Using compact mode for large diff.\n", fg="yellow")

    system_msg = (
        "You are a commit-message assistant.\n"
        "- Provide a concise subject line (imperative mood).\n"
        "- Then include a blank line followed by a detailed multi-line description or bullet list of key changes.\n"
        "- Use Conventional Commits format for the subject: <type>(<scope>): <subject>.\n"
    )
    user_msg = f"Git diff --cached:\n{prompt_diff}"

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.2,
        max_tokens=256
    )
    msg = resp.choices[0].message.content.strip().strip('"')
    return msg


def write_and_edit_message(message):
    """
    Opens the message in $EDITOR for optional editing.
    """
    editor = os.environ.get("EDITOR", "nano")
    with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
        tf.write(message + "\n")
        tf.flush()
        path = tf.name
    code = subprocess.call([editor, path])
    if code != 0:
        return None
    with open(path) as f:
        edited = f.read().strip()
    os.unlink(path)
    return edited if edited and edited != message else None


def commit(message):
    """
    Perform git commit with the provided message.
    """
    try:
        subprocess.check_call(["git", "commit", "-m", message])
        click.secho("Commit successful.\n", fg="green")
    except subprocess.CalledProcessError as e:
        click.secho(f"Git commit failed: {e}\n", fg="red")
        sys.exit(1)


@click.command()
@click.option('--yes', '-y', is_flag=True, help="Skip confirmation and commit immediately.")
def main(yes):
    """
    CLI entry point: stages, generates, and commits with AI-generated message.
    """
    # Stage changes
    try:
        subprocess.check_call(["git", "add", "--all"])
    except subprocess.CalledProcessError:
        click.secho("Failed to stage changes.\n", fg="red")
        sys.exit(1)

    diff = get_staged_diff()
    if not diff:
        click.secho("No changes staged or unable to get diff.\n", fg="yellow")
        sys.exit(1)

    msg = generate_commit_message(diff)
    click.echo(f"\nAI-generated commit message:\n{msg}\n")

    if not yes:
        choice = click.prompt(
            "Options: [y] commit, [e] edit; any other key aborts", 
            default='', 
            show_default=False
        )
        if choice.lower().startswith('e'):
            edited = write_and_edit_message(msg)
            if edited:
                msg = edited
            else:
                click.secho("Edit aborted. Unstaging changes.\n", fg="yellow")
                subprocess.call(["git", "reset", "HEAD"])  # unstage
                sys.exit(0)
        elif not choice.lower().startswith('y'):
            click.secho("Aborting and unstaging.\n", fg="yellow")
            subprocess.call(["git", "reset", "HEAD"])  
            sys.exit(0)

    commit(msg)


if __name__ == "__main__":
    main()
