import os
from src.generate_email import generate_email

def main(newsletter_nb: int=22, branch:str = 'main', email_object: str="[SSPHub] Infolettre de janvier"):
    """
    Extract and add articles from tchap group to veille table on grist

    Args:
        how : choice between 'Test' and 'Veille' modalities

    """
    generate_email(
        number=newsletter_nb,
        branch=branch,
        email_object=f'Pour validation - {email_object}',
        email_to=os.environ["EMAIL_VALIDATION_TO"],
        email_bcc="",
        email_from=None,
        email_cc=os.environ["EMAIL_VALIDATION_CC"] + ";" + os.environ["EMAIL_SSPHUB"],
    )


if __name__ == "__main__":
    try:
        # main("Test")
        main()
    except Exception as e:
        print(f"Fatal error in pipeline: {e}")
        raise
