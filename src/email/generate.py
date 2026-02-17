




def generate_eml_file(
    email_body,
    subject,
    bcc_recipient,
    to_recipient="EMAIL_SSPHUB",
    cc_recipient="",
    from_sender=None,
):
    """
    Creates an .eml file and saves it to .temp/email.eml

    Args:
        email_body (string): html body of the email
        subject (string): Object of the email
        bcc_recipient (string): list of recipients of the emails to put in bcc
        to_recipient (string): Email of the sender to indicate (be cautious, it doesn't automate the sending)
        The email will be sent to himself
        cc_recipient (string): list of recipients of the emails to be put in cc
        from_sender(string or None): email addresses to send from. If None, default Outlook

    Returns:
        None
    Nb : create the email to .temp/email.eml with a message

    Example:
        >>> generate_eml_file('body', 'this an email', 'test@test.fr')
    Email saved as .temp/email.eml
    """
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["BCC"] = bcc_recipient
    msg["CC"] = cc_recipient
    msg["To"] = to_recipient  # Auto send the email
    if from_sender is not None:
        msg["From"] = from_sender  # Set the sender's email address
    msg["X-Unsent"] = (
        "1"  # Mark the email as unsent : when the file is opened, it can be sent.
    )

    # Attach the HTML body
    msg.attach(MIMEText(email_body, "html"))

    # Save the email as an .eml file
    eml_file_path = ".temp/email.eml"

    # Create the output directory if it doesn't exist
    os.makedirs(".temp", exist_ok=True)

    with open(eml_file_path, "wb") as f:
        f.write(msg.as_bytes())

    print(f"Email saved as {eml_file_path}")
