from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import os
import openai
from tenacity import retry, stop_after_attempt, wait_exponential


# Define Pydantic models for the data schema
class FileChange(BaseModel):
    file_path: str
    additions: int
    deletions: int
    code_change: str
    raw_code_original: str
    raw_code_changed: str
    is_visible: bool


class Commit(BaseModel):
    message: str
    description: Optional[str]
    committer_name: str
    is_verified: bool


class GitComparisonSchema(BaseModel):
    num_commits: int
    num_files_changed: int
    commits: List[Commit]
    file_changes: List[FileChange]


# Function to generate comparison URL
def get_comparison_url(git_url: str, start: str, end: str) -> str:
    # Remove .git extension if present
    if git_url.endswith(".git"):
        git_url = git_url[:-4]
    return f"{git_url}/compare/{start}...{end}"


# Retry decorator for API calls
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_openai_api(content: str) -> str:
    """Call OpenAI API with retry logic"""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use an appropriate model
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that formats git commit data into a readable changelog.",
            },
            {"role": "user", "content": content},
        ],
        temperature=0.2,  # Low temperature for consistent output
        max_tokens=6000,
    )

    return response.choices[0].message.content or "N/A"


# Function to generate OpenAI-processed changelog in the custom format
def generate_openai_changelog(
    comparison_data: Dict[str, Any], repo_url: str, start_commit: str, end_commit: str
) -> str:
    if not comparison_data:
        return "No data available to generate changelog."

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        return "Error: OPENAI_API_KEY environment variable not set. Please set it in your .env file."

    # Prepare the data to send to OpenAI
    commits = comparison_data.get("commits", [])
    file_changes = comparison_data.get("file_changes", [])
    
    # Base URL for the repository
    repo_base_url = repo_url.rstrip('/').rstrip('.git')
    
    # Comparison URL to link to the full comparison view
    comparison_url = get_comparison_url(repo_url, start_commit, end_commit)

    # Create a structured input for OpenAI
    prompt = f"""
# Git Comparison Data

Repository: {repo_url}

## Commits Information:
{commits}

## File Changes:
{file_changes}

Please create a detailed changelog in the following format for each commit:

## [[commit-id]]({comparison_url})
Added
[Additions]

Removed
[Removals]

Changed
[Changed]

Fixed
[Fixes]
------------

For each commit:
1. Replace [commit-id] with the commit message but keep it within a markdown link that points to {comparison_url}
   Example: ## [Add new feature for X]({comparison_url})
2. Under "Added", list what was added in the commit (new features, files, functionality)
3. Under "Removed", list what was removed (deleted functionality, deprecated features, removed files)
4. Under "Changed", list what was modified (updates to existing features, refactoring)
5. Under "Fixed", list what was fixed (bug fixes, error corrections)
6. End each commit section with a divider (------------)
7. Focus on making the changelog informative for humans, highlighting important changes
8. Describe code changes in plain language that explains what changed and why it matters
9. If a section has no relevant items (e.g., nothing was added), omit that section entirely

Note: We don't have the exact commit URLs, so we'll link all commit titles to the full comparison page. This helps users access the detailed GitHub comparison view by clicking on any commit title.
"""

    try:
        # Call OpenAI API to generate the formatted changelog
        formatted_changelog = call_openai_api(prompt)

        # Add header and footer
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        header = f"# {repo_name} Changelog (AI-Generated)\n\n"
        header += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        header += f"Comparing [{start_commit}...{end_commit}]({comparison_url})\n\n"

        return header + formatted_changelog

    except Exception as e:
        return f"Error generating AI changelog: {str(e)}"


# Function to generate a formatted changelog from the extracted data
def generate_changelog(
    comparison_data: Dict[str, Any], repo_url: str, start_commit: str, end_commit: str
) -> str:
    if not comparison_data:
        return "No data available to generate changelog."

    # Get the repository name from the URL
    repo_name = repo_url.split("/")[-1].replace(".git", "")

    # Start building the changelog
    changelog = []
    changelog.append(f"# {repo_name} Changelog")

    changelog.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    changelog.append("")

    # Add summary section
    changelog.append("## Summary")
    changelog.append(f"* Total commits: {comparison_data.get('num_commits', 0)}")
    changelog.append(f"* Files changed: {comparison_data.get('num_files_changed', 0)}")
    changelog.append("")

    # Add commit section
    changelog.append("## Commits")
    commits = comparison_data.get("commits", [])
    for i, commit in enumerate(commits):
        message = commit.get("message", "No message")
        description = commit.get("description", "")
        committer = commit.get("committer_name", "Unknown")
        verified = "✓" if commit.get("is_verified", False) else "✗"

        changelog.append(f"### {i+1}. {message}")
        if description:
            changelog.append(f"_{description.strip()}_")
        changelog.append(f"**Author:** {committer} | **Verified:** {verified}")
        changelog.append("")

    # Add file changes section
    changelog.append("## File Changes")
    file_changes = comparison_data.get("file_changes", [])
    for i, file in enumerate(file_changes):
        file_path = file.get("file_path", "Unknown file")
        additions = file.get("additions", 0)
        deletions = file.get("deletions", 0)
        code_change = file.get("code_change", "No change description available")

        changelog.append(f"### {i+1}. {file_path}")
        changelog.append(f"**Changes:** +{additions} / -{deletions}")
        changelog.append("**Description:**")
        changelog.append(f"{code_change}")
        changelog.append("")

    return "\n".join(changelog)


# Function to generate a categorized changelog based on commit types
def generate_categorized_changelog(
    comparison_data: Dict[str, Any], repo_url: str, start_commit: str, end_commit: str
) -> str:
    if not comparison_data:
        return "No data available to generate changelog."

    # Get the repository name from the URL
    repo_name = repo_url.split("/")[-1].replace(".git", "")

    # Start building the changelog
    changelog = []
    changelog.append(f"# {repo_name} Changelog")
    changelog.append(f"### This is a basic changelog generated based on heuristics.")

    changelog.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    changelog.append("")

    # Add summary section
    changelog.append("## Summary")
    changelog.append(f"* Total commits: {comparison_data.get('num_commits', 0)}")
    changelog.append(f"* Files changed: {comparison_data.get('num_files_changed', 0)}")
    changelog.append("")

    # Categorize commits
    feature_commits = []
    bugfix_commits = []
    docs_commits = []
    refactor_commits = []
    test_commits = []
    other_commits = []

    commits = comparison_data.get("commits", [])
    for commit in commits:
        message = commit.get("message", "").lower()

        if any(keyword in message for keyword in ["feat", "feature", "add", "new"]):
            feature_commits.append(commit)
        elif any(
            keyword in message for keyword in ["fix", "bug", "issue", "error", "resolv"]
        ):
            bugfix_commits.append(commit)
        elif any(keyword in message for keyword in ["doc", "readme", "comment"]):
            docs_commits.append(commit)
        elif any(
            keyword in message for keyword in ["refactor", "clean", "restructure"]
        ):
            refactor_commits.append(commit)
        elif any(keyword in message for keyword in ["test", "spec", "assert"]):
            test_commits.append(commit)
        else:
            other_commits.append(commit)

    # Add categorized commit sections
    if feature_commits:
        changelog.append("## ✨ Features")
        for commit in feature_commits:
            message = commit.get("message", "No message")
            description = commit.get("description", "")
            committer = commit.get("committer_name", "Unknown")

            changelog.append(f"* **{message}** - *{committer}*")
            if description and len(description.strip()) > 0:
                changelog.append(f"  - {description.strip()}")
        changelog.append("")

    if bugfix_commits:
        changelog.append("## 🐛 Bug Fixes")
        for commit in bugfix_commits:
            message = commit.get("message", "No message")
            description = commit.get("description", "")
            committer = commit.get("committer_name", "Unknown")

            changelog.append(f"* **{message}** - *{committer}*")
            if description and len(description.strip()) > 0:
                changelog.append(f"  - {description.strip()}")
        changelog.append("")

    if docs_commits:
        changelog.append("## 📄 Documentation")
        for commit in docs_commits:
            message = commit.get("message", "No message")
            description = commit.get("description", "")
            committer = commit.get("committer_name", "Unknown")

            changelog.append(f"* **{message}** - *{committer}*")
            if description and len(description.strip()) > 0:
                changelog.append(f"  - {description.strip()}")
        changelog.append("")

    if refactor_commits:
        changelog.append("## 🔨 Refactoring")
        for commit in refactor_commits:
            message = commit.get("message", "No message")
            description = commit.get("description", "")
            committer = commit.get("committer_name", "Unknown")

            changelog.append(f"* **{message}** - *{committer}*")
            if description and len(description.strip()) > 0:
                changelog.append(f"  - {description.strip()}")
        changelog.append("")

    if test_commits:
        changelog.append("## 🧪 Tests")
        for commit in test_commits:
            message = commit.get("message", "No message")
            description = commit.get("description", "")
            committer = commit.get("committer_name", "Unknown")

            changelog.append(f"* **{message}** - *{committer}*")
            if description and len(description.strip()) > 0:
                changelog.append(f"  - {description.strip()}")
        changelog.append("")

    if other_commits:
        changelog.append("## 🔄 Other Changes")
        for commit in other_commits:
            message = commit.get("message", "No message")
            description = commit.get("description", "")
            committer = commit.get("committer_name", "Unknown")

            changelog.append(f"* **{message}** - *{committer}*")
            if description and len(description.strip()) > 0:
                changelog.append(f"  - {description.strip()}")
        changelog.append("")

    return "\n".join(changelog)
