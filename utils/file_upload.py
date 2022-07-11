import requests,json

def upload_file(image,file_name):
    headers={
        "Authorization": "Bearer 1PfrRiSSFW0AAAAAAAAAAUnWueBZKu0eOz3oxMYnzCJzUMmdaeZcZiaqTYsW_4LM",
        "Dropbox-API-Arg": json.dumps({"path": "/bolpatra/"+file_name, "mode": "add", "autorename": True, "mute": False,"strict_conflict": False}),
        "Content-Type": "application/octet-stream",
    }
    response = requests.post("https://content.dropboxapi.com/2/files/upload", data=image, headers=headers)
    return response


def get_file(file_path):
    headers = {
        "Authorization": "Bearer 1PfrRiSSFW0AAAAAAAAAAUnWueBZKu0eOz3oxMYnzCJzUMmdaeZcZiaqTYsW_4LM",
        "Content-Type": "application/json"
    }
    payload=json.dumps({"path":file_path})
    response = requests.post("https://api.dropboxapi.com/2/files/get_temporary_link", data=payload, headers=headers)
    return response
