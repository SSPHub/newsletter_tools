from src.tchap.message import replace_lines_images, detect_start_image
from src.email.knit import parse_qmd_file, add_link_to_description
from src.github.extract import fetch_qmd_file, raw_url_newsletter, published_url_newsletter

def generate_tchap_message(number):
    """
    Function to generate a text file with the newsletter formatted as a message to
    be sent to Tchap, formatted as qmd.
    Differences from original qmd file are :
    - Images from QMD are removed
    - Description added at top of file

    Args:
        number (int) : infolettre number

    Returns:
        None
        But the messages are printed in a text file in temp folder

    """

    # Fetching published newsletter
    qmd_content = fetch_qmd_file(raw_url_newsletter(number, branch="main"))
    # Extracting content of the newsletter
    qmd_content_lines = parse_qmd_file(qmd_content)[1].split("\n")

    # Removing images
    qmd_content_cleaned_lines = replace_lines_images(qmd_content_lines, detect_start_image(qmd_content_lines))
    cleaned_newsletter = "\n".join(qmd_content_cleaned_lines)

    # Generate description to be added at top of the Tchap message
    description = add_link_to_description(published_url_newsletter(number))

    # Intro message
    message = """Bonjour à tous,

Vous avez dû recevoir l'infolettre dans vos boites mail. Si jamais vous voulez vous inscrire sur la liste de diffusion, c'est par [ici](https://grist.numerique.gouv.fr/o/ssphub/forms/jSjAV3L2F8mmiRVuVEpfF7/103).

Et sinon, la voici en version Tchap (sans les images).
Bonne lecture !
    """

    # Store output
    dest_file = './.temp/chap_message.txt'

    with open(dest_file, 'w') as file:
        file.write(f"{message}\n---\n{description}\n{cleaned_newsletter}")

    print(f"Tchap message generated at {dest_file}")

