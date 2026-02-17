def unzip_dir(zip_file_path, extraction_dir):
    """
    Unzip a folder

    Args:
        zip_file_path (string): path to file to unzip.
        extraction_dir (string): path to directory to unzip files

    Result:
        None. A message is printed

    Example:
        >>> unzip_dir('.temp/Fusion_site_SSPHub-Attachments.zip', '.temp/extracted_data')
        Files extracted to .temp/extracted_data
    """
    # Define the path to the zip file and the extraction directory
    # zip_file_path = '.temp/Fusion_site_SSPHub-Attachments.zip'
    # extraction_dir = '.temp/extracted_data'

    # Remove folder
    remove_files_dir(extraction_dir)

    # Create the extraction directory if it doesn't exist
    if not os.path.exists(extraction_dir):
        os.makedirs(extraction_dir)

    # Open the zip file
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Extract all the contents into the specified directory
        zip_ref.extractall(extraction_dir)

    print(f"Files extracted to {extraction_dir}")


def remove_files_dir(*file_paths):
    """
    Remove files or folder

    Args:
        file_paths (string) : List of files or folder to delete

    Return:
        None

    Example:
        >>> remove_files_dir('.temp/')
        ('.temp/',) have been removed
    """
    for file_path in file_paths:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)
    print(f"{file_paths} have been removed")



def download_file(file_url, output_dir=".temp", headers=None):
    """
    Downloads a file from given url and store it in output_dir

    Arg:
        file_url: url of the file to download, as a string
        output_dir: directory where to save the file to, as a string

    Returns:
        file_name (str): name of the downloaded file
        print if download was successful

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        File downloaded to .temp/2025_09_back_school.png
        '2025_09_back_school.png'
    """

    try:
        # Send a GET request to the GitHub API
        response = requests.get(file_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Extract the file name from the response or, if not, from file_url
        if "Content-Disposition" in response.headers:
            file_name = (
                response.headers["Content-Disposition"]
                .split("filename=")[-1]
                .strip('"')
                .replace(" ", "_")
            )
        else:
            file_name = os.path.basename(file_url)

        # Save the file to the output directory
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"File downloaded to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

    return file_name



