import os
import polars as pl
from src.utils.grist_api import GristApi

def clean_br_values_df(df):
    """
    Replace the /n by HTML <br> mark up or nothing for columns who will end up in a Md table/YAML part

    Args:
        df (pl.Dataframe): the grist table to merge

    Returns;
        df (pl.DataFrame): cleaned df
    """

    # For columns containing 'my table', we replace the break with <br>
    columns_to_replace = [col for col in df.columns if "my_table" in col]

    # Replace '\n' with '<br>' in the identified columns
    for col in columns_to_replace:
        df = df.with_columns(pl.col(col).cast(pl.Utf8).str.replace_all(r"\n", " <br> "))

    # For columns containing 'my yaml', we replace the break with ''
    # columns_to_replace = [col for col in df.columns if 'my_yaml' in col]
    columns_to_replace = ["my_yaml_title", "my_yaml_description"]

    # Replace '\n' with '<br>' in the identified columns
    for col in columns_to_replace:
        df = df.with_columns(pl.col(col).cast(pl.Utf8).str.replace_all(r"\n", " "))

    return df


def fill_template(path_to_template, df, directory_output="newsletter_tools"):
    """
    Update the variables in a template QMD file with the ones from a data table.

    Args:
        df (polars object): data frame where to have the values. A column must be named 'nom_dossier'
        qmd_file (str): The path to the template QMD file. Format 'my_folder/subfolder/template.qmd'
        directory_output (str): A string to paste before nom_dossier. Default is newsletter_tools/nom_dossier/index.qmd'

    """

    # Add directory before the output folder in df
    df = df.with_columns(
        (
            directory_output.strip("/")
            + "/"
            + pl.col("nom_dossier").str.strip_chars_end("/")
        ).alias("nom_dossier")
    )

    for row in df.iter_rows(named=True):
        with open(path_to_template, "r") as file:
            template_content = file.read()

        for column in df.columns:
            variable_name = column
            variable_value = row[column]
            template_content = template_content.replace(
                "{{" + variable_name + "}}", str(variable_value)
            )

        # Create the output directory if it doesn't exist
        os.makedirs(row["nom_dossier"], exist_ok=True)

        output_file_path = row["nom_dossier"] + "/index.qmd"

        # Remove the file and write it
        remove_files_dir(output_file_path)
        with open(output_file_path, "w") as res_file:
            res_file.write(template_content)

        print(f"File written at {output_file_path}")

    return template_content


def get_grist_merge_as_df():
    """
    Get the table from GRIST to fetch all infos about index pages to create

    Arg:
        None

    Returns:
        A pl dataframe with columns matching the template variable names

    Example:
        >>> get_grist_merge_as_df()
    id  ...                                     my_table_title
    0    2  ...  Travaux méthodologiques sur l'enquête Budget d...
    [17 rows x 12 columns]
    """
    # fetch all the rows
    new_website_df = GristApi(os.environ["GRIST_SSPHUB_WEBSITE_MERGE_ID"]).fetch_table_pl("Intranet_details")

    # Selecting useful columns
    cols_to_keep = [
        "id",
        "Acteurs",
        "Resultats",
        "Details_du_projet",
        "sous_titre",
        "Code_du_projet",
        "tags",
        "nom_dossier",
        "date",
        "image",
        "Titre",
        "auteurs",
        "to_update",
    ]

    new_website_df = new_website_df.select(cols_to_keep)

    # Dictionary for renaming variables / Right part must correspond to template keywords
    variable_mapping = {
        "Titre": "my_yaml_title",
        "sous_titre": "my_yaml_description",
        "auteurs": "my_yaml_authors",
        "date": "my_yaml_date",
        "image": "my_yaml_image_path",
        "tags": "my_yaml_categories",
        "Details_du_projet": "my_table_details",
        "Acteurs": "my_table_actors",
        "Resultats": "my_table_results",
        "Code_du_projet": "my_table_repo_path",
    }

    new_website_df = new_website_df.rename(variable_mapping).with_columns(
        pl.col("my_yaml_title").alias("my_table_title")
    )

    return new_website_df


def fill_all_templates_from_grist(
    path_to_template="newsletter_tools/fusion_site/template.qmd",
    directory="newsletter_tools/test",
):
    """
    Fetch information from GRIST to create index.qmd and download the image data, move it to the right folder

    Arg:
        path_to_template (string): the path of the template to use
        directory (string): the root directory where to save the files

    Returns:
        None

    Example:
        >>> fill_all_templates_from_grist()
    """
    # Storing info from GRIST
    pages_df = get_grist_merge_as_df()

    # Cleaning breaks
    pages_df = clean_br_values_df(pages_df)

    # Dropping rows with empty nom_dossier and keeping only the one to_update
    pages_df = pages_df.filter(pl.col("nom_dossier") != "", pl.col("to_update"))

    # Create the index.qmd by calling the function
    fill_template(path_to_template, pages_df, directory_output=directory)

    # Download all attachments in GRIST
    # URL set up
    api_config = GristApi(os.environ['GRIST_SSPHUB_WEBSITE_MERGE_ID'])
    url = api_config.attachment_url
    headers = api_config.headers

    # Destination directory
    temp_dir = ".temp/"
    # Download attachment and store zip file name
    grist_attach_filename = download_file(url, output_dir=temp_dir, headers=headers)

    # Unzip attachment file archive
    unzip_dir_path = temp_dir + "extracted_data"
    unzip_dir(temp_dir + grist_attach_filename, unzip_dir_path)

    # List all images downloaded
    attachments_list = os.listdir(unzip_dir_path)

    # Merging with GRIST data to have destination folder defined in GRIST
    # Creating an intermediate dict
    attachments_dict = {}
    attachments_dict["short_image_name"] = [image[41:] for image in attachments_list]
    attachments_dict["local_image_path"] = [
        unzip_dir_path + "/" + image for image in attachments_list
    ]
    # Selecting the two useful columns
    pages_df = pages_df.select(["nom_dossier", "my_yaml_image_path"])

    # Merging the two and creating destination file
    pages_df = (
        pages_df.join(
            pl.from_dict(attachments_dict),
            how="left",
            left_on="my_yaml_image_path",
            right_on="short_image_name",
        )
        .with_columns(
            (
                directory
                + "/"
                + pl.col("nom_dossier")
                + "/"
                + pl.col("my_yaml_image_path")
            ).alias("dest_image_path")
        )
        .drop_nulls(subset="local_image_path")
    )  # Dropping files where didn't download image

    # Moving all images to their folder
    for row in pages_df.iter_rows(named=True):
        os.rename(row["local_image_path"], row["dest_image_path"])
        print(
            f"File {row['local_image_path']} == moved to ==> {row['dest_image_path']}"
        )

    # Cleaning intermediate data
    remove_files_dir(unzip_dir_path, temp_dir + grist_attach_filename)

