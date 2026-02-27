import os
from src.generate_tchap import generate_tchap_message
import argparse

def main(*args, **kwargs):
    """
    Generate tchap message

    Args:
        See generate_tchap doc

    """
    generate_tchap_message(*args, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Generate tchap message', description='Generate an email from the newsletter stored as a qmd file on the ssphub repo')
    parser.add_argument("-n", "--number", default=22)

    args = parser.parse_args()

    try:
        main(args.number)
    except Exception as e:
        print(f"Fatal error in pipeline: {e}")
        raise


