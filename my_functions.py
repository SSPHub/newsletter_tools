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


##########################################################################################
# Newsletter tools
##########################################################################################


def generate_eml_file(
    email_body,
    subject,
    bcc_recipient,
    to_recipient="EMAIL_SSPHUB",
    cc_recipient="",
    from_sender=None,
):
    """
    Creates an .eml file and saves it to .temp/email.eml

    Args:
        email_body (string): html body of the email
        subject (string): Object of the email
        bcc_recipient (string): list of recipients of the emails to put in bcc
        to_recipient (string): Email of the sender to indicate (be cautious, it doesn't automate the sending)
        The email will be sent to himself
        cc_recipient (string): list of recipients of the emails to be put in cc
        from_sender(string or None): email addresses to send from. If None, default Outlook

    Returns:
        None
    Nb : create the email to .temp/email.eml with a message

    Example:
        >>> generate_eml_file('body', 'this an email', 'test@test.fr')
    Email saved as .temp/email.eml
    """
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["BCC"] = bcc_recipient
    msg["CC"] = cc_recipient
    msg["To"] = to_recipient  # Auto send the email
    if from_sender is not None:
        msg["From"] = from_sender  # Set the sender's email address
    msg["X-Unsent"] = (
        "1"  # Mark the email as unsent : when the file is opened, it can be sent.
    )

    # Attach the HTML body
    msg.attach(MIMEText(email_body, "html"))

    # Save the email as an .eml file
    eml_file_path = ".temp/email.eml"

    # Create the output directory if it doesn't exist
    os.makedirs(".temp", exist_ok=True)

    with open(eml_file_path, "wb") as f:
        f.write(msg.as_bytes())

    print(f"Email saved as {eml_file_path}")


def process_qmd_file_for_email(
    qmd_content,
    qmd_output_file,
    newsletter_url="https://ssphub.netlify.app/infolettre/",
):
    """
    Transform a newsletter qmd file to a qmd file that will be knitted by
    calling the function to transform the yaml part of the qmd file

    Args:
        qmd_content (string): the original qmd file to process, typically the result of fetch_qmd_file
        qmd_output_file (string): the path of the qmd file to write
        newsletter_url (string): to pass the argument onto yaml to insert link to newsletter

    Returns:
        None
    Nb : writes the processed qmd file

    Example:
        >>> process_qmd_file_for_email(
    fetch_qmd_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/index.qmd'),
    'cleaned_index.qmd')
    """

    # qmd_content = fetch_qmd_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/index.qmd')
    # Split the YAML header and the HTML content
    parts = qmd_content.split("---", 2)
    if len(parts) < 3:
        print("Invalid .qmd file format")
        return None

    yaml_header = parts[1]
    html_content = parts[2]

    # Clean the YAML header
    cleaned_yaml_header = clean_yaml_header_for_email(yaml_header, newsletter_url)

    # Combine the cleaned YAML header and HTML content
    processed_qmd_content = f"---\n{cleaned_yaml_header}---\n{html_content}"

    # Save the processed QMD content to a file
    with open(qmd_output_file, "w", encoding="utf-8") as f:
        f.write(processed_qmd_content)


def clean_yaml_header_for_email(yaml_header, newsletter_url):
    """
    Function to transform Yaml header of an index.qmd file and transform it for a qmd file that will be
    knitted to html. It keeps only title, updates the description with the link to the website,
    add lang, format and format options, including a css file.

    Arg :
        yaml_header: input yaml_header to clean, as string
        newsletter_url: url of the newsletter to insert a link to that newsletter

    Returns:
        (string, with Unicode formatting) url to raw Qmd newsletter

    Example:
        >>> clean_yaml_header_for_email(
            '\ntitle: "La rentrée 2025:"\n\ndescription: |\n  Infolettre de __Septembre 2025__
            \n\n# Date published\ndate: \'2025-09-29\'\nnumber: 19\n\nauthors:\n  - Nicolas\n\nimage: mage.png\n\ntags:\n
            - datavis\n  - IA \n\ncategories:\n  - Infolettre\n\n',
            'https://ssphub.netlify.app/infolettre/'
            )
        "title: 'La rentrée 2025:'\ndescription: '*Infolettre de __Septembre 2025__ disponible sur le site du [réseau](https://ssphub.netlify.app/infolettre/)*'\nlang: fr\nformat:\n  html:\n    self-contained: true\n    css: ../newsletter_tools/email/css/style.css\n"

    """

    # Parse the YAML header1
    yaml_data = yaml.safe_load(yaml_header)

    # Keep only the specified keys
    # We put the link
    description = (
        "*"
        + yaml_data.get("description", "").strip()
        + " disponible sur le site du [réseau]("
        + newsletter_url
        + ")*"
    )

    cleaned_yaml = {
        "title": yaml_data.get("title", "").strip(),
        "description": description,
    }

    # Add missing params
    cleaned_yaml["lang"] = "fr"
    cleaned_yaml["format"] = {
        "html": {
            "self-contained": True,  # To have images inside the email
            "css": "../newsletter_tools/email/css/style.css",
        }
    }

    # Convert the cleaned YAML back to a string
    cleaned_yaml_str = yaml.dump(
        cleaned_yaml, sort_keys=False, allow_unicode=True, width=4096
    )
    return cleaned_yaml_str


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


def list_image_files_for_newsletter(number, branch="main"):
    """
    Wrapper of list_raw_image_files. List image files present in the github folder InseeFrLab, repo ssphub. Ima

    Arg :
        number of the newsletter
        branch where the newsletter is (main by default)

    Returns:
        list of path to the raw images files

    Example:
        >>> list_image_files_for_newsletter('19', branch='main')
        ['https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png',
        'https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/measles-cases-historical-us-states-heatmap.png']

    """
    repo_owner = "InseeFrLab"
    repo_name = "ssphub"
    subfolder_path = f"infolettre/infolettre_{number}"

    return list_raw_image_files(repo_owner, repo_name, subfolder_path, branch)


def download_images_for_newsletter(number, branch="main", output_dir=".temp"):
    """
    Download all image files from given newsletter number and branch and store it in output_dir

    Arg:
        number: number of the newsletter whose images will be downloaded, as a string
        branch: repo branch of the newsletter (main for published newsletter, other for non published newsletters)
        output_dir: directory where to save the files to, as a string

    Returns:
        nothing
        nb : a message is printed if download was successful

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        Image file downloaded to .temp/2025_09_back_school.png
    """
    # Get the list of image files in the subfolder
    image_files = list_image_files_for_newsletter(number, branch)

    if not image_files:
        print("No image files found in the subfolder.")

    # Download each image file
    downloaded_files = []
    for image_file_url in image_files:
        downloaded_file = download_file(image_file_url, output_dir)
        if downloaded_file:
            downloaded_files.append(downloaded_file)

    return downloaded_files


def generate_email(
    number,
    branch,
    email_object,
    email_to,
    email_bcc,
    email_from="SELECT THE RIGHT EMAIL",
    email_cc="",
    drop_temp=True,
):
    """
    Generates the draft email for a newsletter in the folder '.temp/'. Built on previous functions.

    Arg:
        number (string): number of the newsletter to turn into email
        branch (string): repo branch of the newsletter to turn into email (main for published newsletter, other for non published newsletters)
        email_object (string): object of the email
        email_to (string) : list of email addresses to send the email to
        email_bcc (string) : list of email addresses to be in bcc
        email_from(string) : sender to see in Outlook. None for default sender
        email_cc (string) : list of email addresses to be in cc
        drop_temp (boolean): if temporary knitted files should be removed after knitting. Default is true

    Returns:
        None

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        Image file downloaded to .temp/2025_09_back_school.png
    """
    temp_file = "./.temp/temp"
    temp_file_qmd = temp_file + ".qmd"
    temp_file_html = temp_file + ".html"

    download_images_for_newsletter(number, branch, ".temp")

    qmd_content = fetch_qmd_file(raw_url_newsletter(number, branch))
    process_qmd_file_for_email(
        qmd_content, temp_file_qmd, published_url_newsletter(number)
    )
    knit_to_html(temp_file_qmd)

    with open(temp_file_html, "r", encoding="utf-8") as f:
        generate_eml_file(
            f.read(),
            email_object,
            email_bcc,
            to_recipient=email_to,
            cc_recipient=email_cc,
            from_sender=email_from,
        )

    if drop_temp:
        remove_files_dir(temp_file_qmd, temp_file_html)






if __name__ == "__main__":
    remove_files_dir(".temp/", "newsletter_tools/test/")

    fill_all_templates_from_grist()
    generate_email(
        19, "main", "Infolettre de rentrée", "my_to_email@insee.fr", get_emails()
    )

    remove_files_dir(".temp/", "newsletter_tools/test/")
