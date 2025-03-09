# GitHub Changelog Generator

A powerful Streamlit application that generates comprehensive changelogs by analyzing git commit differences between two references.

## 🌟 Features

- **Visual Git Comparison**: Compare any two commits or references from a GitHub repository
- **Detailed Change Information**: Extract detailed information about commits and file changes
- **Multiple Changelog Formats**:
  - **Standard Changelog**: A traditional chronological listing of commits and changes
  - **Categorized Changelog**: Changes organized by type (features, bugfixes, docs, etc.)
  - **AI-Processed Changelog**: An intelligent, structured changelog created using OpenAI
    - Clearly separates additions, removals, changes, and fixes
    - Focuses on human-readable summaries over technical details
- **Easy to Use**: Simple interface with download options for all generated changelogs

## 📋 Requirements

- Python 3.8+
- Streamlit
- Hyperbrowser API key
- OpenAI API key (for AI-processed changelogs)

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd github-changelog-generator
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   HYPERBROWSER_API_KEY=your_hyperbrowser_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```

## 🚀 Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. In your browser, enter:
   - A GitHub repository URL (e.g., `https://github.com/username/repo`)
   - Starting commit hash/reference (e.g., `v1.0` or a commit hash)
   - Ending commit hash/reference (e.g., `main` or a commit hash)

3. Click "View Comparison" to generate changelogs

4. Navigate between the different tabs to view different changelog formats:
   - **Detailed View**: Browse commits and file changes with expandable sections
   - **Standard Changelog**: A traditional chronological changelog
   - **Categorized Changelog**: Changes organized by type (features, bugfixes, etc.)
   - **AI-Processed Changelog**: An intelligent changelog with additions, removals, changes, and fixes clearly separated
   - **Raw Data**: View the raw JSON data

5. Download any changelog format using the provided download buttons

## 📊 Changelog Formats

### Standard Changelog
A traditional changelog that lists all commits chronologically with their associated file changes.

### Categorized Changelog
Organizes commits into categories based on their type:
- ✨ Features
- 🐛 Bug Fixes
- 📄 Documentation
- 🔨 Refactoring
- 🧪 Tests
- 🔄 Other Changes

### AI-Processed Changelog
Uses OpenAI to generate a human-readable changelog that clearly separates:
- **Added**: New features, files, or functionality
- **Removed**: Deleted functionality, deprecated features, or files
- **Changed**: Updates to existing features or refactoring
- **Fixed**: Bug fixes and error corrections

## 🧩 Project Structure

- `app.py`: Main Streamlit application
- `changelog_generator.py`: Core logic for generating changelogs
- `requirements.txt`: Project dependencies

## ⚙️ How It Works

1. The application uses Hyperbrowser to extract git comparison data from GitHub
2. It processes this data to extract commits, file changes, additions, and deletions
3. Various changelog formats are generated based on this data
4. For AI-processed changelogs, the data is sent to OpenAI's API to generate more human-friendly descriptions

## 📝 License

[MIT License](LICENSE)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](link-to-issues).
