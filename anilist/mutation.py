from authenticate import get_headers
import requests
from rich import print
import json

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
    data = requests.post(
        url, json={"query": query, "variables": variables}, headers=get_headers()
    )
    return json.loads(data.text)