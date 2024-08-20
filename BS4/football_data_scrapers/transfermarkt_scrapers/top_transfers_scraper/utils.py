import re

def get_image_filename(image_url: str, player_name: str) -> str:
    '''
    Returns the filename that should be used for the image.
    Filename is determined by concatenating players name and
    the file extension extracted with re from the given URL
    '''
    regex = re.compile(r'(\.[a-zA-Z]{3,4})(?=\?lm=1)')
    match = regex.search(image_url)
    if match:
        file_extension = match[1].lower()
        filename = player_name + file_extension
        return filename
    else:
        print(f"There was an error while finding {player_name} image's filename")
        return f'{player_name}_unknown_extension.jpg'