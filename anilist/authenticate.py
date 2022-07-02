def save_token():
    import webbrowser
    url = f"https://anilist.co/api/v2/oauth/authorize?client_id=8068&response_type=token"
    webbrowser.open(url)
    with open(r".\anilist\access_token.txt", "w") as f:
        f.write(input("Paste the access token here: "))

def get_token():
    with open(r".\anilist\access_token.txt") as f:
        access_token = f.read()
    return access_token