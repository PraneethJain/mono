from .authenticate import get_headers
from requests import post
from json import loads

url = "https://graphql.anilist.co"


def set_progress(mediaId, progress):
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
    data = post(
        url, json={"query": query, "variables": variables}, headers=get_headers()
    )
    return loads(data.text)
