import os

import requests


def list_github_branches(repo_owner: str, repo_name: str):
    """
    Lists all branches of a GitHub repository.

    Args:
        repo_owner (str): Owner of the repository.
        repo_name (str): Name of the repository.

    Returns:
        list: List of branch names.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/branches"

    response = requests.get(url)

    if response.status_code == 200:
        branches = response.json()
        return [branch["name"] for branch in branches]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")


def extract_branch_max_nb(branches_list: list):
    """
    Returns the highest number from branch names starting with "infolettre_".

    Args:
        branches_list: List of branch names (e.g., ["infolettre_1", "infolettre_2"]).

    Returns:
        int: Highest number extracted from matching branch names.
    """
    pattern = "infolettre_"
    nb_list = [
        int(branch[len(pattern) :])
        for branch in branches_list
        if branch.startswith(pattern)
    ]
    number = max(nb_list)

    return f"{pattern}{number}", number


def list_raw_files(repo_owner, repo_name, subfolder_path, branch="main"):
    """
    List files and folder present in a given github folder.

    Arg :
        repo_owner : name of the owner of the repo in Github
        repo_name : name of the Github repo
        subfolder_path : in the given repo architecture, a subfolder path to the folder where you want to list all files.
    For example : infolettre/infolettre_19/
        branch where the newsletter is (main by default)

    Returns:
        url to the raw files
        Output format: a list of strings

    Example:
        >>> list_raw_files('InseeFrLab', 'ssphub', 'infolettre/infolettre_19', branch='main')
        [{'name': '2025_09_back_school.png', 'path': 'infolettre/infolettre_19/2025_09_back_school.png',
        'sha': 'd2efaee464a794eba9f31f68068f95198e77c777', 'size': 1492220, 'url': 'https://api.github.com/
        repos/InseeFrLab/ssphub/contents/infolettre/infolettre_19/2025_09_back_school.png?ref=main', ...]
    """
    # GitHub API URL to list contents of a subfolder
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{subfolder_path}?ref={branch}"

    try:
        # Send a GET request to the GitHub API
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching contents from GitHub API: {e}")
        return None


def list_raw_image_files(repo_owner, repo_name, subfolder_path, branch="main"):
    """
    List image files present in a given github folder. Images are defined by the following formats
    ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')

    Arg :
        repo_owner : name of the owner of the repo in Github
        repo_name : name of the Github repo
        subfolder_path : in the given repo architecture, a subfolder path to the folder where you want to list all files.
    For example : infolettre/infolettre_19/
        branch where the newsletter is (main by default)

    Returns:
        url to the raw images files
        Output format: a list of strings

    Example:
        >>> list_raw_image_files('InseeFrLab', 'ssphub', 'infolettre/infolettre_19', branch='main')
        ['https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png',
        'https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/measles-cases-historical-us-states-heatmap.png']

    """
    # Get the file lists
    contents = list_raw_files(
        repo_owner=repo_owner,
        repo_name=repo_name,
        subfolder_path=subfolder_path,
        branch=branch,
    )

    # Filter image files (assuming common image extensions)
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"}
    image_files = [
        f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/refs/heads/{branch}/{item['path']}"
        for item in contents
        if item["type"] == "file"
        and os.path.splitext(item["name"])[1].lower() in image_extensions
    ]

    return image_files


def fetch_qmd_file(url):
    """
    get the qmf file from an url and return it as string

    Args:
        url (string): the qmd url to fetch. Usually a github raw URL

    Returns:
        (string) the text of the qmd file

    Example:
        >>> fetch_qmd_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/index.qmd')
    '---\ntitle: "La rentrée 2025: actualités, nouveautés, interview de rentrée"\n\ndescription: |\n  Infolettre du mois de
    __Septembre 2025__\n\n# Date published\ndate: \'2025-09-29\'\nnumber: 19\n\nauthors:\n ......'
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the .qmd file: {e}")
        return None


def raw_url_newsletter(number, branch="main"):
    """
    Function to get url of raw Qmd files of a newsletter on SSPHub repo

    Arg :
        number: number of the newsletter
        branch: branch of the repo to look for

    Returns:
        (string) Url to raw Qmd newsletter
    """
    return f"https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/{branch}/infolettre/infolettre_{number}/index.qmd"


def published_url_newsletter(number):
    """
    Function to generate url of published newsletter on SSPHub website

    Arg :
        number: number of the newsletter

    Returns:
        url to ssphub website of the given newsletter
        Output format: a string

    Example:
        >>> published_url_newsletter('19')
        'https://ssphub.netlify.app/infolettre/infolettre_19/'
    """
    return f"https://ssphub.netlify.app/infolettre/infolettre_{number}/"
