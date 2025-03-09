import io
import re
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


import streamlit as st
from hyperbrowser import Hyperbrowser
from hyperbrowser.models.extract import StartExtractJobParams

# Import the changelog generator module
from changelog_generator import (
    generate_changelog,
    generate_categorized_changelog,
    generate_openai_changelog,
    GitComparisonSchema,
    get_comparison_url,
)


# Function to validate GitHub URL
def is_valid_github_url(url: str) -> bool:
    github_pattern = re.compile(r"^https?://github\.com/[\w\-]+/[\w\-]+(\.git)?$")
    return bool(re.match(github_pattern, url))


# Function to extract git comparison data using Hyperbrowser
@st.cache_data
def extract_git_comparison(comparison_url: str) -> Optional[Dict[str, Any]]:
    try:
        # Initialize Hyperbrowser client
        api_key = os.getenv("HYPERBROWSER_API_KEY")
        if not api_key:
            st.error(
                "HYPERBROWSER_API_KEY environment variable not set. Please set it in a .env file."
            )
            return None

        client = Hyperbrowser(api_key=api_key, base_url="http://localhost:8080")
        print(
            comparison_url,
        )
        # Create extract job
        result = client.extract.start_and_wait(
            params=StartExtractJobParams(
                urls=[comparison_url],
                schema=GitComparisonSchema,
                prompt="""
                Extract the following information from this GitHub comparison page:
                1. The total number of commits in this comparison
                2. The total number of files changed
                3. For each commit:
                   - The main commit message (title)
                   - The commit description (body, if any)
                   - The name of the committer
                   - Whether the commit is verified (true/false)
                4. For each file changed:
                   - The file path
                   - The number of additions (green lines)
                   - The number of deletions (red lines)
                   - A summary of the actual changes
                   - Whether the commit change is visible in the UI (true/false)
                """,
                wait_for=None,
            )
        )
        print(result.job_id)
        print(result.data)
        return result.data

    except Exception as e:
        st.error(f"Error extracting data: {str(e)}")
        return None


if __name__ == "__main__":
    st.set_page_config(
        layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
        initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
        page_title="Changelog Builder - Hyperbrowser",  # String or None. Strings get appended with "• Streamlit".
        page_icon="https://hyperbrowser-assets-bucket.s3.us-east-1.amazonaws.com/favicon.ico",  # String, anything supported by st.image, or None.
    )

    # Create two columns for the header
    col1, col2 = st.columns([3, 2])

    # Add logo in the left column - using local file
    with col1:
        st.image(
            "https://hyperbrowser-assets-bucket.s3.us-east-1.amazonaws.com/wordmark-dark.png",
            width=200,
        )

    # Add hyperbrowser link in the right column, aligned to the right
    with col2:
        st.html(
            """
        <div style="text-align: right; display: flex; justify-content: flex-end; height: 100%; align-items: center;">
            <p style="margin: 0px;">
                Powered by <a href="https://hyperbrowser.ai" target="_blank">hyperbrowser.ai</a>
            </p>
        </div>
        """,
        )

    st.title("GitHub Commit Comparison Viewer")
    # Input field for repository URL
    git_url: str = st.text_input(
        "Git Repository URL (e.g., https://github.com/username/repo)"
    )
    # Create two columns for start and end commit inputs
    col1, col2 = st.columns(2)
    with col1:
        starting_commit: str = st.text_input("Starting Commit Hash/Reference")
    with col2:
        ending_commit: str = st.text_input("Ending Commit Hash/Reference")

    # Main execution
    if st.button("View Comparison") and git_url and starting_commit and ending_commit:
        if not is_valid_github_url(git_url):
            st.error("Please enter a valid GitHub repository URL")
        else:
            comparison_url: str = get_comparison_url(
                git_url, starting_commit, ending_commit
            )
            with st.spinner("Extracting commit comparison data..."):
                comparison_data = extract_git_comparison(comparison_url)
                if comparison_data:
                    st.success("Successfully extracted commit comparison data")

                    # Generate changelogs
                    standard_changelog = generate_changelog(
                        comparison_data, git_url, starting_commit, ending_commit
                    )
                    categorized_changelog = generate_categorized_changelog(
                        comparison_data, git_url, starting_commit, ending_commit
                    )

                    # Create tabs for different views
                    tab3, tab2, tab1, tab4 = st.tabs(
                        [
                            "AI-Processed Changelog",
                            "Commit Diff View",
                            "Categorized Changelog",
                            "Raw Data",
                        ]
                    )

                    repo_name = git_url.split("/")[-1].replace(".git", "")

                    with tab1:
                        # Display summary information
                        st.subheader("Summary")
                        st.write(
                            f"**Number of commits:** {comparison_data.get('num_commits', 0)}"
                        )
                        st.write(
                            f"**Number of files changed:** {comparison_data.get('num_files_changed', 0)}"
                        )

                        # Display commit information
                        st.subheader("Commits")
                        commits = comparison_data.get("commits", [])
                        for i, commit in enumerate(commits):
                            with st.expander(
                                f"Commit {i+1}: {commit.get('message', 'No message')}"
                            ):
                                st.write(f"**Message:** {commit.get('message', 'N/A')}")
                                st.write(
                                    f"**Description:** {commit.get('description', 'N/A')}"
                                )
                                st.write(
                                    f"**Committer:** {commit.get('committer_name', 'N/A')}"
                                )
                                st.write(
                                    f"**Verified:** {'Yes' if commit.get('is_verified', False) else 'No'}"
                                )

                        # Display file changes
                        st.subheader("File Changes")
                        file_changes = comparison_data.get("file_changes", [])
                        for i, file in enumerate(file_changes):
                            with st.expander(
                                f"File {i+1}: {file.get('file_path', 'Unknown file')}"
                            ):
                                st.write(
                                    f"**File path:** {file.get('file_path', 'N/A')}"
                                )
                                st.write(f"**Additions:** {file.get('additions', 0)}")
                                st.write(f"**Deletions:** {file.get('deletions', 0)}")
                                st.write(
                                    f"**Changes:** {file.get('code_change', 'N/A')}"
                                )
                                st.code(
                                    file.get("raw_code_original", "N/A"),
                                    language="diff",
                                )
                                st.code(
                                    file.get("raw_code_changed", "N/A"), language="diff"
                                )
                                st.write(
                                    f"**Visible in UI:** {'Yes' if file.get('is_visible', True) else 'No'}"
                                )

                    with tab2:
                        # Display the categorized changelog
                        st.markdown(categorized_changelog)

                        # Add download button for the categorized changelog
                        categorized_data = io.BytesIO(categorized_changelog.encode())
                        st.download_button(
                            label="Download Categorized Changelog",
                            data=categorized_data,
                            file_name=f"{repo_name}_categorized_changelog_{starting_commit}_to_{ending_commit}.md",
                            mime="text/markdown",
                        )

                    with tab3:
                        # Check if OpenAI API key is set
                        if not os.getenv("OPENAI_API_KEY"):
                            st.warning(
                                "OpenAI API key not found. Please add your API key to the .env file as OPENAI_API_KEY=your_key_here"
                            )
                            st.text(
                                "Example .env file content:\nOPENAI_API_KEY=sk-your-key-here\nHYPERBROWSER_API_KEY=your-hyperbrowser-key"
                            )
                        else:
                            with st.spinner("Generating AI-processed changelog..."):
                                # Generate the OpenAI-processed changelog
                                openai_changelog = generate_openai_changelog(
                                    comparison_data,
                                    git_url,
                                    starting_commit,
                                    ending_commit,
                                )

                                # Display the OpenAI-processed changelog
                                st.markdown(openai_changelog)

                                # Add download button for the OpenAI-processed changelog
                                openai_data = io.BytesIO(openai_changelog.encode())
                                st.download_button(
                                    label="Download AI-Processed Changelog",
                                    data=openai_data,
                                    file_name=f"{repo_name}_ai_changelog_{starting_commit}_to_{ending_commit}.md",
                                    mime="text/markdown",
                                )

                    with tab4:
                        # Display raw JSON data
                        st.json(comparison_data)

                    # Provide a direct link
                    st.markdown(f"[Open comparison in browser]({comparison_url})")
