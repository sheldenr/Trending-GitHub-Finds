import os
import sys
import yaml
import requests
from datetime import datetime

# GitHub API Headers
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# Language Badge Colors (Shields.io colors)
LANG_COLORS = {
    "Python": "3776AB",
    "TypeScript": "3178C6",
    "JavaScript": "F7DF1E",
    "Go": "00ADD8",
    "Rust": "000000",
    "C++": "00599C",
    "Java": "007396",
    "Swift": "FA7343",
    "Kotlin": "7F52FF",
    "Ruby": "CC342D",
    "PHP": "777BB4",
    "HTML": "E34F26",
    "CSS": "1572B6",
    "Shell": "89E051",
    "Zig": "EC915C",
    "Lua": "2C2D72",
}

def get_repo_data(repo_full_name):
    """Fetch repository metadata from GitHub API."""
    url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {repo_full_name}: {response.status_code}")
        return None

def format_stars(stars):
    """Format star count (e.g., 1.2k)."""
    if stars >= 1000:
        return f"{stars/1000:.1f}k"
    return str(stars)

def generate_row(repo_name, user_note, repo_data):
    """Generate a Markdown table row for a repository."""
    if not repo_data:
        return f"| [{repo_name}](https://github.com/{repo_name}) | {user_note} | Unknown | ⭐ - |"

    description = repo_data.get("description", user_note)
    if not description:
        description = user_note
    
    lang = repo_data.get("language", "Unknown")
    color = LANG_COLORS.get(lang, "lightgrey")
    lang_badge = f"![{lang}](https://img.shields.io/badge/{lang}-{color}?style=flat-square&logo={lang.lower().replace('+', 'plus').replace('#', 'sharp')}&logoColor=white)"
    
    stars = format_stars(repo_data.get("stargazers_count", 0))
    repo_url = repo_data.get("html_url", f"https://github.com/{repo_name}")
    
    return f"| [{repo_name}]({repo_url}) | {description} | {lang_badge} | ⭐ {stars} |"

def update_readme(config_path, readme_path):
    """Update README.md based on finds.yml."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    new_content = [
        "# 🌟 Trending Repo Finds\n\n",
        "A curated collection of the most interesting, innovative, and game-changing repositories found on GitHub Trending. This repository is updated regularly to keep track of the latest in open-source.\n\n",
        "---\n\n",
        "## 📑 Table of Contents\n"
    ]

    # Generate TOC
    for category in config.keys():
        anchor = category.lower().replace(" ", "-").replace("&", "").replace("--", "-")
        new_content.append(f"- [{category}](#{anchor})\n")
    
    new_content.append("\n---\n")

    # Generate sections based on config
    for category, repos in config.items():
        new_content.append(f"\n## {category}\n")
        new_content.append(f"| Repository | Description | Language | Stats |\n")
        new_content.append(f"| :--- | :--- | :--- | :--- |\n")
        
        for repo_entry in repos:
            if isinstance(repo_entry, dict):
                repo_name = list(repo_entry.keys())[0]
                user_note = repo_entry[repo_name]
            else:
                repo_name = repo_entry
                user_note = ""
            
            print(f"Processing {repo_name}...")
            repo_data = get_repo_data(repo_name)
            new_content.append(generate_row(repo_name, user_note, repo_data) + "\n")
        
        new_content.append("\n---\n")

    # Add the "How to Update" and Footer sections
    new_content.append("\n## 📈 How to Update\n")
    new_content.append("1. Add a repository to `finds.yml`.\n")
    new_content.append("2. Run `python3 update_list.py`.\n\n")
    new_content.append("```bash\npython3 update_list.py\n```\n\n")
    new_content.append("---\n\n## 🤝 Contributing\nFound a cool repository? Open a PR!\n\n---\n\n## 📜 License\nMIT © [Your Name]\n")

    with open(readme_path, "w") as f:
        f.writelines(new_content)

if __name__ == "__main__":
    update_readme("finds.yml", "README.md")
