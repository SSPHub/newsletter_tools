# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "email-mime",
#     "os",
#     "pyyaml",
#     "requests",
#     "grist-api",
#     "polars",
# ]
# ///

from email.mime.multipart import MIMEMultipart  # To generate the draft email
from email.mime.text import MIMEText  # To generate the draft email
import requests  # To transform newsletter into email, call Github API and download files
import yaml  # To update newsletter qmd metadata for the email
import os  # to remove temporary files, create directory etc
from grist_api import GristDocAPI  # To get directory emails
import polars as pl  # to manage directory emails
import re  # For pattern matching to search for emails
import shutil  # to remove directory and its content
import zipfile  # GRIST attachments

##########################################################################################
# Common tools
##########################################################################################


def fetch_grist_table_as_pl(doc_grist_id, table_id):
    """
    Get a grist table as a polar dataframe. It transforms Grist records :
    - If the value is a list (not a tuple) and the first element is 'L', we want an
      array of all elements 1...end

    Args:
        doc_grist_id : id of the grist document
        table_id (string) : id of the Grist table

    Return:
        A pl dataframe
    """
    grist_api = get_dinum_grist_login(doc_grist_id)
    table_grist_records = grist_api.fetch_table(table_id)
    table_dict = [record._asdict() for record in table_grist_records]

    # Cleaning Grist lists - causes a pb with polars. from
    # https://github.com/uaw-union/sheets-parquet-server/blob/19acaa3ef9ab65f9229b3df5e7007b8cc1fffca0/src/main.py#L4
    transformed_records = [
        {
            k: (
                ";".join([str(s) for s in v])
                if isinstance(v, list) and len(v) > 0
                else v
            )
            for k, v in d.items()
        }
        for d in table_dict
    ]

    return pl.DataFrame(transformed_records, infer_schema_length=None)


def get_dinum_grist_login(doc_grist_id):
    """
    Send back GRIST API login details

    Args:
        None

    Returns:
        A GristDocAPI object
    """
    # Log in to GRIST API
    SERVER = "https://grist.numerique.gouv.fr/"

    if "GRIST_API_KEY" not in os.environ:
        raise ValueError("The GRIST_API_KEY environment variable does not exist.")

    # Returning API details connection
    return GristDocAPI(doc_grist_id, server=SERVER)


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


def knit_to_html(processed_qmd_file):
    """
    knit a qmd file to html

    Args:
        processed_qmd_file (string): file path to the qmd file to knit

    Returns:
        None
    Saves the knitted file with same name as qmd file, same folder
    """
    # Use the Quarto CLI to knit the QMD file to HTML
    import subprocess

    try:
        subprocess.run(
            ["quarto", "render", processed_qmd_file, "--to", "html"], check=True
        )
        print("QMD file successfully knitted to HTML")
    except subprocess.CalledProcessError as e:
        print(f"Error knitting QMD file to HTML: {e}")


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


def download_file(file_url, output_dir=".temp", headers=None):
    """
    Downloads a file from given url and store it in output_dir

    Arg:
        file_url: url of the file to download, as a string
        output_dir: directory where to save the file to, as a string

    Returns:
        file_name (str): name of the downloaded file
        print if download was successful

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        File downloaded to .temp/2025_09_back_school.png
        '2025_09_back_school.png'
    """

    try:
        # Send a GET request to the GitHub API
        response = requests.get(file_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Extract the file name from the response or, if not, from file_url
        if "Content-Disposition" in response.headers:
            file_name = (
                response.headers["Content-Disposition"]
                .split("filename=")[-1]
                .strip('"')
                .replace(" ", "_")
            )
        else:
            file_name = os.path.basename(file_url)

        # Save the file to the output directory
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"File downloaded to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

    return file_name


def unzip_dir(zip_file_path, extraction_dir):
    """
    Unzip a folder

    Args:
        zip_file_path (string): path to file to unzip.
        extraction_dir (string): path to directory to unzip files

    Result:
        None. A message is printed

    Example:
        >>> unzip_dir('.temp/Fusion_site_SSPHub-Attachments.zip', '.temp/extracted_data')
        Files extracted to .temp/extracted_data
    """
    # Define the path to the zip file and the extraction directory
    # zip_file_path = '.temp/Fusion_site_SSPHub-Attachments.zip'
    # extraction_dir = '.temp/extracted_data'

    # Remove folder
    remove_files_dir(extraction_dir)

    # Create the extraction directory if it doesn't exist
    if not os.path.exists(extraction_dir):
        os.makedirs(extraction_dir)

    # Open the zip file
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Extract all the contents into the specified directory
        zip_ref.extractall(extraction_dir)

    print(f"Files extracted to {extraction_dir}")


def remove_files_dir(*file_paths):
    """
    Remove files or folder

    Args:
        file_paths (string) : List of files or folder to delete

    Return:
        None

    Example:
        >>> remove_files_dir('.temp/')
        ('.temp/',) have been removed
    """
    for file_path in file_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)
    print(f"{file_paths} have been removed")





if __name__ == "__main__":
    remove_files_dir(".temp/", "newsletter_tools/test/")

    fill_all_templates_from_grist()
    generate_email(
        19, "main", "Infolettre de rentrée", "my_to_email@insee.fr", get_emails()
    )

    remove_files_dir(".temp/", "newsletter_tools/test/")
