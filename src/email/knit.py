import yaml
import subprocess


def parse_qmd_file(qmd_content):
    """
    Splits the YAML header and the md content from a qmd file

    Args:
        qmd_content (string): the original qmd file to process, typically the result of fetch_qmd_file

    Returns:
        a tuple of
        (
            yaml_header,
            html_content
        )
    """
    parts = qmd_content.split("---", 2)
    if len(parts) < 3:
        print("Invalid .qmd file format")
        return None

    yaml_header = parts[1]
    html_content = parts[2]

    return yaml_header, html_content


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
    yaml_header, html_content = parse_qmd_file(qmd_content)

    # Clean the YAML header
    cleaned_yaml_header = clean_yaml_header_for_email(yaml_header, newsletter_url)

    # Combine the cleaned YAML header and HTML content
    processed_qmd_content = f"---\n{cleaned_yaml_header}---\n{html_content}"

    # Save the processed QMD content to a file
    with open(qmd_output_file, "w", encoding="utf-8") as f:
        f.write(processed_qmd_content)


def add_link_to_description(newsletter_url, yaml_data={"description": "Infolettre"}):
    """
    Add to the description keys of a dict the link to the url of the newsletter

    Arg :
        newsletter_url: url of the newsletter to insert a link to that newsletter
        yaml_data: a dict with a description key

    Returns:
        (string) updated description field with link to newsletter
    """
    description = (
        "*"
        + yaml_data.get("description", "").strip()
        + " disponible sur le site du [réseau]("
        + newsletter_url
        + ")*"
    )

    return description


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
        "title: 'La rentrée 2025:'\ndescription: '*Infolettre de __Septembre 2025__ disponible sur le site du [réseau](https://ssphub.netlify.app/infolettre/)*'\nlang: fr\nformat:\n  html:\n    self-contained: true\n    css: ../email/css/style.css\n"

    """

    # Parse the YAML header1
    yaml_data = yaml.safe_load(yaml_header)

    # Keep only the specified keys
    # Transform the description file
    description = add_link_to_description(
        newsletter_url,
        yaml_data=yaml_data
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
            "css": "../email/css/style.css",
        }
    }

    # Convert the cleaned YAML back to a string
    cleaned_yaml_str = yaml.dump(
        cleaned_yaml, sort_keys=False, allow_unicode=True, width=4096
    )
    return cleaned_yaml_str



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
    try:
        subprocess.run(
            ["quarto", "render", processed_qmd_file, "--to", "html"], check=True
        )
        print("QMD file successfully knitted to HTML")
    except subprocess.CalledProcessError as e:
        print(f"Error knitting QMD file to HTML: {e}")
