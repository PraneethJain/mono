from .authenticate import get_headers
from datetime import timedelta
import requests
import json

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
                            timeUntilAiring
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


def get_air_time(mediaId: int, ep_num: int):
    query = """
    query ($mediaId: Int, $episode: Int) {
        AiringSchedule (mediaId: $mediaId, episode: $episode) {
            timeUntilAiring
        }
    }
    """
    variables = {"mediaId": mediaId, "episode": ep_num}
    data = requests.post(
        url, json={"query": query, "variables": variables}, headers=get_headers()
    )
    return timedelta(
        seconds=json.loads(data.text)["data"]["AiringSchedule"]["timeUntilAiring"]
    )
