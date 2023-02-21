import webbrowser
import json
import os
import httpx
import info


class Anilist:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(headers=self.get_headers())
        self.url = "https://graphql.anilist.co"

    def get_token(self) -> None:
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

    def get_headers(self) -> dict[str, str]:
        """
        Returns headers required to make authorized requests
        """

        self.get_token()

        with open(info.data_path, "r") as f:
            token = json.load(f)["token"]

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def close(self) -> None:
        await self.client.aclose()

    async def get_user_data(self) -> dict:
        """
        Returns the authenticated user's data, including user id and account statistics.
        """

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

        r = await self.client.post(self.url, json={"query": query})

        return json.loads(r.text)["data"]["Viewer"]

    async def get_user_list(self) -> list[dict]:
        """
        Returns the authenticated user's CURRENT list, containing details of the anime.
        """
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
        variables = {"userId": (await self.get_user_data())["id"], "status": "CURRENT"}
        r = await self.client.post(
            self.url, json={"query": query, "variables": variables}
        )

        return json.loads(r.text)["data"]["MediaListCollection"]["lists"][0]["entries"]

    async def set_progress(self, mediaId: int, progress: int) -> dict:
        """
        Sets the progress of the anime with `mediaId` to `progress`
        """

        query = """
        mutation ($mediaId: Int, $progress: Int) {
            SaveMediaListEntry(mediaId: $mediaId, progress: $progress) {
                mediaId
                id
                status
                progress
            }
        }
        """
        variables = {"mediaId": mediaId, "progress": progress}

        r = await self.client.post(
            self.url, json={"query": query, "variables": variables}
        )
        return json.loads(r.text)


ani = Anilist()
