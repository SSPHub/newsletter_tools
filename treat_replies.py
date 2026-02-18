import os
from src.directory.replies import delete_email_from_contact_table
import argparse

def main(*args):
    """
    Treat replies

    Args:
        See delete_email_from_contact_table doc

    """
    delete_email_from_contact_table(*args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Treat non working emails', description='Deletes emails from directory table')
    parser.add_argument("-f", "--file_path", default="replies.txt")

    args = parser.parse_args()

    try:
        main(args.file_path)
    except Exception as e:
        print(f"Fatal error in pipeline: {e}")
        raise


