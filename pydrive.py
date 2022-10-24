from uuid import uuid4
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def login_with_service_account():
    settings = {
        "client_config_backend": "service",
        "service_config": {
            "client_json_file_path": "credentials.json",
        }
    }
    # Create instance of GoogleAuth
    gauth = GoogleAuth(settings=settings)
    # Authenticate
    gauth.ServiceAuth()
    return gauth


gauth = login_with_service_account()
drive = GoogleDrive(gauth)


def upload_file(path: str, title: str):
    file = drive.CreateFile(
        {"title": title, "parents": [{"kind": "drive#fileLink", 'teamDriveId': "0AMQ275zHBB7zUk9PVA", "id": "1TCimBq8GinCDyigH1_2oEouf1CkHIxnA"}]})
    file.SetContentFile(path)
    file.Upload(param={'supportsTeamDrives': True})
    return title
