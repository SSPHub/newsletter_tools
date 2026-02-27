import os
from src.generate_email import generate_email
from src.directory.extract import get_emails
import argparse

def main(*args, **kwargs):
    """
    Generate email based on generate_email

    Args:
        See generate_email doc

    """
    generate_email(*args, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Generate email', description='Generate an email from the newsletter stored as a qmd file on the ssphub repo')
    parser.add_argument("-n", "--number", default=22)
    parser.add_argument("-b", "--branch", default="main")
    parser.add_argument("-o", "--email_object", default="[SSPHub] Infolettre de janvier")
    parser.add_argument("-to", "--email_to", default=os.environ['EMAIL_SSPHUB'])
    parser.add_argument("-bcc", "--email_bcc", default=get_emails())
    parser.add_argument("-from", "--email_from", default="")
    parser.add_argument("-cc", "--email_cc", default="")
    parser.add_argument("-t", "--drop_temp", default="False")

    args = parser.parse_args()

    try:
        main(args.number, args.branch, args.email_object, args.email_to, args.email_bcc, args.email_from, args.email_cc, args.drop_temp == "True")
    except Exception as e:
        print(f"Fatal error in pipeline: {e}")
        raise


