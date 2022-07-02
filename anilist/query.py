from authenticate import get_token
import requests
import json
from rich import print

url = "https://graphql.anilist.co"


def get_headers():
    return {
        "Authorization": "Bearer " + get_token(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def get_user_data():
    query = """
    query {
        Viewer {
            id
            name
            about
            statistics {
                anime {
                    count
                    minutesWatched
                    episodesWatched
                }
            }
            siteUrl
            createdAt
            updatedAt
        }
    }
    """
    data = requests.post(url, json={"query": query}, headers=get_headers())
    return json.loads(data.text)["data"]


print(get_user_data())
