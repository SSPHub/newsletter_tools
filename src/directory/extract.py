import os
import polars as pl
from src.utils.grist_api import GristApi


def get_directory_as_df():
    """
    Fetch back directory of SSPHUB and management as a pl dataframe

    Args:
        None

    Returns:
        A pl.DataFrame with three columns : ['Email', 'Nom', 'Nom_domaine', 'Supprimez_mon_compte']
    """
    # Selecting set of columns
    cols_to_keep = ["Email", "Nom", "Nom_domaine", "Supprimez_mon_compte"]

    # fetch all the rows of general enlisted persons
    directory_df = (
        GristApi(os.environ["GRIST_SSPHUB_DIRECTORY_ID"])
        .fetch_table_pl("Contact")
        .select(cols_to_keep)
    )

    # Fetching data for management
    # Selecting set of columns
    cols_to_keep = ["Email", "Nom", "Nom_domaine"]

    directory_df_mngmt = (
        GristApi(os.environ["GRIST_SSPHUB_DIRECTORY_ID"]).fetch_table_pl("Encadrement_SSMs")
        .select(cols_to_keep)
        .with_columns(Supprimez_mon_compte=False)
    )

    return pl.concat([directory_df, directory_df_mngmt])


def get_emails():
    """
    Extract all emails that have not asked to be deteled from directory

    Returns:
        a single string with joined emails separated by ;

    Example:
        >>> get_emails()
        '<myemail@example.com>; <myemail2@example.com>'
    """
    my_directory_df = (
        get_directory_as_df()
        .filter(~pl.col("Supprimez_mon_compte"))  # ~ is equivalent to not
        .unique(subset="Email")
        .sort(["Nom_domaine", "Nom"])
        .with_columns(Email="<" + pl.col("Email") + ">")  # Turning emails from myemail@example.com to <myemail@example.com>
    )

    # Joining all emails into one string '<myemail@example.com>; <myemail2@example.com>'
    return "; ".join(my_directory_df["Email"])
