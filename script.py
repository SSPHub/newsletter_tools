import src.main as my_f
import src.directory.replies as post_tr
import os

# import importlib  # To reload package
# importlib.reload(my_f)  # When functions are updated
import os

# To generate email
newsletter_nb = 22
email_object = "[SSPHub] Infolettre de janvier"

## Validation
my_f.generate_email(
    number=newsletter_nb,
    branch=f'newsletter_{newsletter_nb}',
    email_object=f'Pour validation - {email_object}',
    email_to=os.environ["EMAIL_VALIDATION_TO"],
    email_bcc="",
    email_from=None,
    email_cc=os.environ["EMAIL_VALIDATION_CC"] + ";" + os.environ["EMAIL_SSPHUB"],
)

## Once cleared, accept the PR. Once PR done, send to all
my_f.generate_email(
    number=newsletter_nb,
    branch="main",
    email_object=email_object,
    email_to=os.environ["EMAIL_SSPHUB"],
    email_bcc=my_f.get_emails(),
    email_from="SELECT THE RIGHT EMAIL"
)

# ## Treat replies
# post_tr.delete_email_from_contact_table(file_path="newsletter_tools/replies.txt")

