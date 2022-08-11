import json


def get_token():
    import webbrowser

    url = (
        f"https://anilist.co/api/v2/oauth/authorize?client_id=8068&response_type=token"
    )
    webbrowser.open(url)
    return input("Paste the access token here: ")


def get_headers():
    with open("app/data/config.json") as f:
        TOKEN: str = json.load(f)["access_token"]
    return {
        "Authorization": "Bearer " + TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
