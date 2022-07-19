from .authenticate import get_headers
import requests
import json
from rich import print

url = "https://graphql.anilist.co"


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
    return json.loads(data.text)["data"]["Viewer"]


def get_user_list(status: str):
    query = """
    query ($userId: Int, $status: MediaListStatus) {
        MediaListCollection (userId: $userId, status: $status, type: ANIME) {
            lists {
                name
                entries {
                    media {
                        id
                        title {
                            romaji
                            english
                            native
                            userPreferred
                        }
                        format
                        status
                        description (asHtml: false)
                        startDate {day month year}
                        endDate {day month year}
                        season
                        seasonYear
                        episodes
                        duration
                        source
                        mediaListEntry {
                            progress
                        }
                        nextAiringEpisode {
                            airingAt
                            episode
                        }
                    }
                }
            }
        }
    }
    """
    variables = {"userId": get_user_data()["id"], "status": status}
    data = requests.post(
        url, json={"query": query, "variables": variables}, headers=get_headers()
    )
    return json.loads(data.text)["data"]["MediaListCollection"]["lists"][0]
