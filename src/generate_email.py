from src.email.generate import generate_eml_file
from src.email.knit import knit_to_html, process_qmd_file_for_email
from src.email.prep import download_images_for_newsletter
from src.github.extract import (
    extract_branch_max_nb,
    fetch_qmd_file,
    list_github_branches,
    published_url_newsletter,
    raw_url_newsletter,
)
from src.utils.files import remove_files_dir


def generate_email(
    email_object,
    email_to,
    email_bcc,
    email_from="SELECT THE RIGHT EMAIL",
    email_cc="",
    drop_temp=True,
    number=None,
    branch=None,
):
    """
    Generates the draft email for a newsletter in the folder '.temp/'. Built on previous functions.

    Arg:
        email_object (string): object of the email
        email_to (string) : list of email addresses to send the email to
        email_bcc (string) : list of email addresses to be in bcc
        email_from(string) : sender to see in Outlook. None for default sender
        email_cc (string) : list of email addresses to be in cc
        drop_temp (boolean): if temporary knitted files should be removed after knitting. Default is true
        number (string): number of the newsletter to turn into email
        branch (string): repo branch of the newsletter to turn into email (main for published newsletter, other for non published newsletters)

    Returns:
        None

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        Image file downloaded to .temp/2025_09_back_school.png
    """
    temp_file = "./.temp/temp"
    temp_file_qmd = temp_file + ".qmd"
    temp_file_html = temp_file + ".html"

    repo_owner = "InseeFrLab"
    repo_name = "ssphub"

    if branch is None:
        branches_list = list_github_branches(repo_owner, repo_name)
        branch, number = extract_branch_max_nb(branches_list)

    download_images_for_newsletter(number, branch, ".temp", repo_owner, repo_name)

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
