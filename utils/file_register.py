from utils.file_upload import upload_file
import json
import boto3
from django.conf import settings
import time


def register_files(request):
    for file in request.FILES:
        register_file = request.FILES[file].read()
        file_name = request.data.get(file).name
        document = upload_file(register_file, file_name)
        byte_to_json = json.loads(
            document._content.decode('utf8').replace("'", '"'))
        file_path = byte_to_json["path_lower"]
        request.data[file] = file_path


def register_file(file):
    timestamp = int(time.time())
    file_name = f"{str(timestamp)}_{file.name}"
    s3_path= f"{settings.AWS_LOCATION}{file_name}"
    register_file = file.read()
    session = boto3.Session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    s3 = session.client("s3")
    s3.put_object(Body = register_file, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_path)
    return settings.MEDIA_URL + file_name
