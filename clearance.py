import argparse
import os

from src.generate_email import generate_email


def main(*args, **kwargs):
    """
    Generate email based on generate_email

    Args:
        See generate_email doc

    """
    generate_email(*args, **kwargs)


if __name__ == "__main__":
    emails_cc = os.environ["EMAIL_VALIDATION_CC"] + ";" + os.environ["EMAIL_SSPHUB"]
    parser = argparse.ArgumentParser(
        prog="Generate clearance email",
        description="Generate an email from the newsletter stored as a qmd file on the ssphub repo",
    )
    parser.add_argument("-n", "--number", default=None)
    parser.add_argument("-b", "--branch", default=None)
    parser.add_argument(
        "-o", "--email_object", default="[SSPHub] Pour validation - infolettre"
    )
    parser.add_argument("-to", "--email_to", default=os.environ["EMAIL_VALIDATION_TO"])
    parser.add_argument("-bcc", "--email_bcc", default="")
    parser.add_argument("-from", "--email_from", default="")
    parser.add_argument("-cc", "--email_cc", default=emails_cc)
    parser.add_argument("-t", "--drop_temp", default=True)

    args = parser.parse_args()

    try:
        main(
            args.email_object,
            args.email_to,
            args.email_bcc,
            args.email_from,
            args.email_cc,
            args.drop_temp,
            args.number,
            args.branch,
        )
    except Exception as e:
        print(f"Fatal error in pipeline: {e}")
        raise
