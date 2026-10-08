import os

UPLOAD_DIR = "/var/app/uploads"


def read_upload(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "rb") as f:
        return f.read()
