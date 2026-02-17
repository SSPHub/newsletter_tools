
def raw_url_newsletter(number, branch="main"):
    """
    Function to get url of raw Qmd files of a newsletter on SSPHub repo

    Arg :
        number: number of the newsletter
        branch: branch of the repo to look for

    Returns:
        (string) Url to raw Qmd newsletter
    """
    return f"https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/{branch}/infolettre/infolettre_{number}/index.qmd"


def published_url_newsletter(number):
    """
    Function to generate url of published newsletter on SSPHub website

    Arg :
        number: number of the newsletter

    Returns:
        url to ssphub website of the given newsletter
        Output format: a string

    Example:
        >>> published_url_newsletter('19')
        'https://ssphub.netlify.app/infolettre/infolettre_19/'
    """
    return f"https://ssphub.netlify.app/infolettre/infolettre_{number}/"


def list_image_files_for_newsletter(number, branch="main"):
    """
    Wrapper of list_raw_image_files. List image files present in the github folder InseeFrLab, repo ssphub. Ima

    Arg :
        number of the newsletter
        branch where the newsletter is (main by default)

    Returns:
        list of path to the raw images files

    Example:
        >>> list_image_files_for_newsletter('19', branch='main')
        ['https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png',
        'https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/measles-cases-historical-us-states-heatmap.png']

    """
    repo_owner = "InseeFrLab"
    repo_name = "ssphub"
    subfolder_path = f"infolettre/infolettre_{number}"

    return list_raw_image_files(repo_owner, repo_name, subfolder_path, branch)


def download_images_for_newsletter(number, branch="main", output_dir=".temp"):
    """
    Download all image files from given newsletter number and branch and store it in output_dir

    Arg:
        number: number of the newsletter whose images will be downloaded, as a string
        branch: repo branch of the newsletter (main for published newsletter, other for non published newsletters)
        output_dir: directory where to save the files to, as a string

    Returns:
        nothing
        nb : a message is printed if download was successful

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        Image file downloaded to .temp/2025_09_back_school.png
    """
    # Get the list of image files in the subfolder
    image_files = list_image_files_for_newsletter(number, branch)

    if not image_files:
        print("No image files found in the subfolder.")

    # Download each image file
    downloaded_files = []
    for image_file_url in image_files:
        downloaded_file = download_file(image_file_url, output_dir)
        if downloaded_file:
            downloaded_files.append(downloaded_file)

    return downloaded_files
