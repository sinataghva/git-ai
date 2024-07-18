# Git Automation Scripts

This repository contains two Python scripts that help automate Git operations using the OpenAI API: `gitlog.py` and `gitcommit.py`. These scripts simplify generating human-readable release notes and commit messages by leveraging the power of AI.

## Disclaimer

These scripts are provided as a proof of concept to demonstrate what is possible. There is no guarantee that they will work exactly as intended. Users are responsible for any consequences of sending their code diffs or commit messages to the OpenAI API. Use these scripts at your own risk, especially on sensitive projects. Users should provide their own OpenAI API key and respect their organization's AI policies regarding the use of AI tools.

## Scripts Overview

### `gitlog.py`

This script generates a non-technical, human-readable summary of Git commits for inclusion in release notes. It uses the OpenAI API to convert technical commit details into concise summaries understandable by non-technical users.

#### Features
- Fetches Git log entries with custom formatting.
- Generates a clear and concise summary of the commits.
- Allows filtering commits by date, commit range, author, or grep pattern.
- Can generate technical summaries for release notes.
- Designed for inclusion in release notes for internal use.

#### Usage

1. Run the script in your repository:

    - To get commits since a specific date:

        ```sh
        python gitlog.py --since-date 2023-01-01
        ```

    - To get commits within a specific range:

        ```sh
        python gitlog.py --range start_commit..end_commit
        ```

    - To get commits by a specific author:

        ```sh
        python gitlog.py --author "John Doe"
        ```

    - To get commits with a specific grep pattern:

        ```sh
        python gitlog.py --grep "BUGFIX"
        ```

    - To generate a technical summary:

        ```sh
        python gitlog.py --technical
        ```

### `gitcommit.py`

This script generates concise and precise commit messages based on the changes in your Git repository. It stages all changes, generates a commit message using the OpenAI API, and allows you to review, edit, or abort the commit process.

#### Features
- Stages all changes (`git add .`).
- Generates a commit message based on the Git diff.
- Allows reviewing and editing the generated commit message.
- Aborts the commit and unstages all changes if needed.

#### Usage

1. Run the script in your repository:

    ```sh
    python gitcommit.py
    ```

2. Review the commit message:
    - The script will generate a commit message and prompt you to:
        - Use the generated commit message.
        - Edit the commit message in your default text editor.
        - Abort the commit.

3. **Editing in `nano`**:
    - If you choose to edit, `nano` will open with the generated commit message.
    - To abort during editing, exit `nano` without saving changes (Ctrl + X, then N).

4. **Abort Handling**: If you abort, the script will unstage all changes.

## Setting Up

1. **Install Python**: Ensure you have Python installed on your system.
2. **Install OpenAI Client and python-dotenv**: Install the OpenAI Python client library and `python-dotenv` which helps in loading environment variables from a `.env` file.

    ```sh
    pip install openai python-dotenv
    ```

3. **Set OpenAI API Key**: Copy the `.env.example` file to `.env` and add your OpenAI API key:

    ```sh
    cp .env.example .env
    ```

    Edit the `.env` file to add your OpenAI API key:

    ```plaintext
    OPENAI_API_KEY=your-api-key
    ```

### macOS Users

If you are using macOS, you may need to use `python3` and `pip3` instead of `python` and `pip`. Additionally, since the Python environment can be managed by the OS, it is recommended to create a virtual environment before installing packages.

1. **Create a Virtual Environment**:

    ```sh
    python3 -m venv venv
    ```

2. **Activate the Virtual Environment**:

    ```sh
    source venv/bin/activate
    ```

3. **Install OpenAI Client and python-dotenv**:

    ```sh
    pip3 install openai python-dotenv
    ```

