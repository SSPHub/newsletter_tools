import re  # For pattern matching to search for emails
import os
import polars as pl
from src.utils.grist_api import GristApi

def extract_emails_from_txt(file_path="newsletter_tools/test/replies.txt"):
    """
    Extract all email addresses from a file that contains all the automatic replies to a newsletter / an email.

    Args:
        file_path (str): The path to the file containing email addresses.

    Returns:
        list: A list of extracted email addresses.
    """
    # Regular expression pattern for matching email addresses
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    # Read the content of the file
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Find all email addresses in the content
    emails = re.findall(email_pattern, content)

    # Remove duplicate - Convert the list of email addresses to a set and back to list
    emails = set(emails)
    emails = list(emails)

    # Turn to lowercase
    emails = [s.lower() for s in emails]

    return emails


def get_ids_of_email(emails_list):
    """
    Return the ids of the rows of the email in the GRIST directory. Will return a list of length 0 if an email is not in the list.

    Args:
        emails_list (list) : a list of strings, containing the emails to look for in df

    Returns:
        a polars dataframe with id and Email columns

    Example:
        >>> get_ids_of_email(['test1@insee.fr', 'test2@insee.fr'])
        []
    """
    # Get the latest GRIST directory
    directory_df = (
        GristApi(os.environ["GRIST_SSPHUB_DIRECTORY_ID"])
        .fetch_table_pl("Contact")
        .select(["id", "Email"])
        .with_columns(
            pl.col("Email").str.to_lowercase()  # to lowercase for email matching
        )
    )

    # Filter the emails
    res = directory_df.filter(pl.col("Email").is_in(emails_list))

    return res


def delete_email_from_contact_table(file_path):
    """
    Takes a txt file as input and delete the detected email from the Contacts table of Grist

    Args:
        file_path (string): path to the txt file to extract emails from

    Return:
        None
    """
    emails_list = extract_emails_from_txt(file_path)
    directory_df = get_ids_of_email(emails_list)
    emails_id = directory_df["id"].to_list()
    GristApi(os.environ["GRIST_SSPHUB_DIRECTORY_ID"]).delete_records(
        "Contact", json=emails_id
    )

    # Managing output
    print_df = pl.DataFrame({"Email":emails_list})
    print_df = (
        directory_df
        .join(print_df, how="right", on="Email")
        .fill_null(value="non")
        .select("Email", "id")
        .rename({"Email":"Email détecté réponses", "id":"détecté_annuaire"})
    )
    pl.Config.set_tbl_rows(print_df.height)
    print(f"{print_df}")
    print(f"{print_df.height} emails détectés dans les réponses")
    print(f"{print_df["détecté_annuaire"].drop_nulls().len()} emails supprimés de la table Contact\n")

