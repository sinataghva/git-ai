import subprocess
import tempfile
import os

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()

def stage_all_changes():
    try:
        subprocess.run(['git', 'add', '--all'], check=True)
        print("All changes have been staged.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while staging changes: {e.stderr}")
        return False
    return True

def unstage_all_changes():
    try:
        subprocess.run(['git', 'reset'], check=True)
        print("All changes have been unstaged.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while unstaging changes: {e.stderr}")

def get_git_diff():
    try:
        result = subprocess.run(['git', 'diff', '--cached'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running git diff: {e.stderr}")
        return None

def generate_commit_message(git_diff):
    system_message = {
        "role": "system", 
        "content": "Generate a concise and precise commit message based on the provided Git diff. The message should be clear and not too long."
    }
    user_message = {
        "role": "user", 
        "content": f"Git diff:\n{git_diff}\n\nGenerate a concise commit message:"
    }

    response = client.chat.completions.create(
        model="gpt-4o",  # Adjust model if needed
        messages=[system_message, user_message]
    )

    return response.choices[0].message.content.strip().strip('\"')

def edit_commit_message(initial_message):
    with tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.tmp') as tmpfile:
        tmpfile.write(initial_message)
        tmpfile.flush()
        editor = os.getenv('EDITOR', 'nano')
        exit_code = subprocess.run([editor, tmpfile.name]).returncode

        tmpfile.seek(0)
        edited_message = tmpfile.read()
        
    os.unlink(tmpfile.name)
    if exit_code != 0 or edited_message.strip() == initial_message.strip():
        return None
    return edited_message.strip()


def commit_changes(commit_message):
    try:
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print(f"Committed with message: {commit_message}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while committing: {e.stderr}")

if __name__ == "__main__":
    if stage_all_changes():
        git_diff = get_git_diff()
        if git_diff:
            commit_message = generate_commit_message(git_diff)
            if commit_message:
                print(f"Generated Commit Message:\n{commit_message}")
                confirm = input("Do you want to use this commit message? (yes/no/edit): ").strip().lower()
                if confirm == 'yes':
                    commit_changes(commit_message)
                elif confirm == 'edit':
                    edited_message = edit_commit_message(commit_message)
                    if edited_message:
                        commit_changes(edited_message)
                    else:
                        print("Commit aborted during edit.")
                        unstage_all_changes()
                else:
                    print("Commit aborted.")
                    unstage_all_changes()
