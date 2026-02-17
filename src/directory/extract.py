import os
import polars as pl

def get_directory_as_df():
    """
    Fetch back directory of SSPHUB and management as a pl dataframe

    Args:
        None

    Returns:
        A pl.DataFrame with three columns : ['Email', 'Nom', 'Nom_domaine', 'Supprimez_mon_compte']
    """
    # fetch all the rows of general enlisted persons
    directory_df = fetch_grist_table_as_pl(
        os.environ["GRIST_SSPHUB_DIRECTORY_ID"], "Contact"
    )

    # Selecting set of columns
    cols_to_keep = ["Email", "Nom", "Nom_domaine", "Supprimez_mon_compte"]

    directory_df = directory_df.select(cols_to_keep)

    # Fetching data for management
    # Selecting set of columns
    cols_to_keep = ["Email", "Nom", "Nom_domaine"]

    directory_df_mngmt = (
        fetch_grist_table_as_pl(
            os.environ["GRIST_SSPHUB_DIRECTORY_ID"], "Encadrement_SSMs"
        )
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
    my_directory_df = get_directory_as_df()
    my_directory_df = (
        my_directory_df.filter(~pl.col("Supprimez_mon_compte"))  # ~ is equivalent to not
        .unique(subset="Email")
        .sort(["Nom_domaine", "Nom"])
    )
    # Turning emails from myemail@example.com to <myemail@example.com>
    my_directory_df.with_columns("<" + pl.col("Email") + ">")
    # Joining all emails into one string '<myemail@example.com>; <myemail2@example.com>'
    return "; ".join(my_directory_df["Email"])
