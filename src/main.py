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
