import webbrowser
import info
import json
import os


def get_token() -> None:
    """
    Retrieves the token and writes it to the users appdata, if not present already.
    """

    if not os.path.exists(info.data_dir):
        os.makedirs(info.data_dir)

        webbrowser.open(
            "https://anilist.co/api/v2/oauth/authorize?client_id=8068&response_type=token"
        )

        with open(info.data_path, "w") as f:
            json.dump({"token": input("Paste access token here: ")}, f)


def get_headers() -> dict[str, str]:
    """
    Returns headers required to make authorized requests
    """

    get_token()

    with open(info.data_path, "r") as f:
        token = json.load(f)["token"]

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
