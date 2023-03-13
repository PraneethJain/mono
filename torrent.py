from qbittorrent import Client
from info import data_path
from json import load
from os import path
from urllib3 import disable_warnings

disable_warnings(ResourceWarning)


class Torrent:
    try:
        client = Client("http://127.0.0.1:8080/")
    except:
        raise ConnectionError("Open qbittorent web user interface and restart.")

    client.login("admin", "adminadmin")

    def __init__(
        self,
        series: str,
        *,
        magnet: str | None = None,
        infohash: str | None = None,
    ) -> None:
        self.series = series
        self.magnet = magnet
        with open(data_path, "r") as f:
            data = load(f)

        self.download_path = path.join(
            data["download_path"], self.sanitize_filename(series)
        )

        if infohash is None:
            self.client.download_from_link(self.magnet, savepath=self.download_path)
            self.infohash = self.client.torrents(sort="added_on", reverse=True)[0][
                "hash"
            ]
        else:
            self.infohash = infohash

    def get_download_percentage(self) -> float:
        data = self.client.get_torrent(self.infohash)
        return data["total_downloaded"] / data["total_size"] * 100

    def is_completed(self) -> bool:
        return self.client.get_torrent(self.infohash)["completion_date"] != -1

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        keepcharacters = (" ", ".", "_")
        return "".join(
            c for c in filename if c.isalnum() or c in keepcharacters
        ).rstrip()


if __name__ == "__main__":
    infohash = "6b673ee96b32559808bfe71198c0fb43bd13fabe"
    series = "Otonari no Tenshi-sama ni Itsunomanika Dame Ningen ni Sareteita Ken"

    t = Torrent(series, infohash=infohash)
