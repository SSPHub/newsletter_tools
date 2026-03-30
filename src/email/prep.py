from src.github.extract import list_raw_image_files
from src.utils.files import download_file


def download_images_for_newsletter(
    number, branch="main", output_dir=".temp", repo_owner="InseeFrLab", repo="ssphub"
):
    """
    Download all image files from given newsletter number and branch and store it in output_dir

    Arg:
        number: number of the newsletter whose images will be downloaded, as a string
        branch: repo branch of the newsletter (main for published newsletter, other for non published newsletters)
        output_dir: directory where to save the files to, as a string
        repo_owner (str) : repo owner to go to
        repo (str) : repo_name

    Returns:
        nothing
        nb : a message is printed if download was successful

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        Image file downloaded to .temp/2025_09_back_school.png
    """
    # Get the list of image files in the subfolder
    image_files = list_raw_image_files(
        repo_owner, repo, f"infolettre/infolettre_{number}", branch
    )

    if not image_files:
        print("No image files found in the subfolder.")

    # Download each image file
    downloaded_files = []
    for image_file_url in image_files:
        downloaded_file = download_file(image_file_url, output_dir)
        if downloaded_file:
            downloaded_files.append(downloaded_file)

    return downloaded_files
