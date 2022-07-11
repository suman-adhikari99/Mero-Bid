import json
from utils.file_upload import get_file


def generate_link(file):
    link = get_file(file)
    byte_to_json = json.loads(
        link._content.decode('utf8').replace("'", '"'))
    return byte_to_json['link']
