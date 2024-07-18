import subprocess
import argparse

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

def get_git_log(since_date=None, range_commits=None, author=None, grep=None):
    git_command = ['git', 'log', '--color', '--date=local',
                   "--pretty=format:'%C(red)%h%C(reset)%C(yellow)%d%C(reset) %s %C(green)(%cr) %C(magenta)(%cd) %C(bold blue)<%an>%C(reset)'",
                   '--graph']

    # filter on date
    if since_date:
        git_command.extend(['--since', since_date])

    # filter on commit range
    if range_commits:
        git_command.extend([range_commits])

    #  filter on author
    if author:
        git_command.extend(['--author', author])

    # filter on commit message grep pattern
    if grep:
        git_command.extend(['--grep', grep])

    try:
        result = subprocess.run(git_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running git log: {e.stderr}")
        return None

def generate_summary(commit_log, start_text, is_technical):
    system_message = {
        "role": "system", 
        "content": "I have a list of Git commits from a software project. Each commit includes technical details about code changes, bug fixes, and feature implementations. I need a concise, non-technical summary of these commits for inclusion in release notes. The summary should be straightforward, avoiding any promotional or marketing language. Focus on summarizing the key changes and improvements."
    }

    # System message for technical summary:
    technical_system_message = {
        "role": "system",
        "content": (
            "I have a detailed list of Git commits from this week. Each commit includes technical details such as code diffs, "
            "bug fixes, and refactorings. Provide a technical summary that clearly lists the factual changes (e.g., modified functions, "
            "updated files, refactored modules) without using superfluous adjectives or vague terminology. Focus solely on what was changed."
        )
    }

    user_message = {
        "role": "user", 
        "content": f"Here is the list of commits:\n\n{commit_log}\n\nBased on this list of commits, generate a non-technical summary for the release notes. Start the summary with '{start_text}'"
    }

    messages = [system_message, user_message]
    if is_technical:
        messages[0] = technical_system_message

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate release notes from Git log.')
    parser.add_argument('--since-date', help='Fetch commits since this date (YYYY-MM-DD)')
    parser.add_argument('--range', help='Fetch commits in this range (start_commit..end_commit)')
    parser.add_argument('--author', help='Fetch commits by this author')
    parser.add_argument('--grep', help='Fetch commits with this grep pattern')
    parser.add_argument('--technical', help='Generate technical summary for release notes', action='store_true')

    args = parser.parse_args()

    since_date = args.since_date
    range_commits = args.range

    filters = []
    if since_date:
        filters.append(f"since {since_date}")
    if range_commits:
        filters.append(f"in {range_commits}")
    if args.author:
        filters.append(f"by {args.author}")
    if args.grep:
        filters.append(f"with grep {args.grep}")
    if args.technical:
        filters.append("(technical)")

    if filters:
        start_text = "What's changed " + " ".join(filters) + ":"
    else:
        start_text = "What's changed:"

    git_log = get_git_log(since_date=since_date, range_commits=range_commits, author=args.author, grep=args.grep)
    if git_log:
        summary = generate_summary(git_log, start_text, args.technical)
        print("Release Notes Summary:")
        print(summary)