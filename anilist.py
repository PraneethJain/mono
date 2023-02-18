import webbrowser
import json
import os
import httpx
import info


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


async def get_user_data() -> dict:
    """
    Returns the authenticated user's data, including user id and account statistics.
    """

    url = "https://graphql.anilist.co"
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

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={"query": query}, headers=get_headers())

    return json.loads(r.text)["data"]["Viewer"]


async def get_user_list() -> list[dict]:
    """
    Returns the authenticated user's CURRENT list, containing details of the anime.
    """
    url = "https://graphql.anilist.co"
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
                        description
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
    variables = {"userId": (await get_user_data())["id"], "status": "CURRENT"}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            url, json={"query": query, "variables": variables}, headers=get_headers()
        )

    return json.loads(r.text)["data"]["MediaListCollection"]["lists"][0]["entries"]
