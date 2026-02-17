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



if __name__ == "__main__":
    remove_files_dir(".temp/", "newsletter_tools/test/")

    fill_all_templates_from_grist()
    generate_email(
        19, "main", "Infolettre de rentrée", "my_to_email@insee.fr", get_emails()
    )

    remove_files_dir(".temp/", "newsletter_tools/test/")
