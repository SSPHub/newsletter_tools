

def detect_start_image(qmd_content_lines):
    """
    Function to detect lines that start with images syntax ![

    Args
        qmd_content_lines (list of string): a list of strings, each element of the list representing a line

    Returns:
        list of integer, representing index of the input list matching the pattern
    """

    images_lines_index = [index for index, line in enumerate(qmd_content_lines) if line[:2] == "!["]

    return images_lines_index


def replace_lines_images(qmd_content_lines, images_lines_index):
    """
    Function to replace
    """

    for lines_to_replace_index in images_lines_index:
        text_replaced = qmd_content_lines[lines_to_replace_index][2:]  # droping first 2 characters ![
        text_replaced = text_replaced.split("](")  # splitting for legend with urls
        text_replaced = text_replaced[:-1]  # removing link of url ](my_url)
        text_replaced = "](".join(text_replaced)  # rejoining whole legend together
        text_replaced = "Image provenant de :" + text_replaced  # add to say it's a picture

        qmd_content_lines[lines_to_replace_index] = text_replaced

    return qmd_content_lines


