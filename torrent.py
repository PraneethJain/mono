from qbittorrent import Client
from info import data_path
from json import load
from urllib3 import disable_warnings

disable_warnings(ResourceWarning)


class Torrent:
    client = Client("http://127.0.0.1:8080/")
    client.login("admin", "adminadmin")

    def __init__(self, series: str, magnet: str) -> None:
        self.series = series
        self.magnet = magnet
        with open(data_path, "r") as f:
            data = load(f)

        self.download_path = (
            f"{data['download_path']}\\{self.sanitize_filename(series)}"
        )
        self.client.download_from_link(self.magnet, savepath=self.download_path)
        self.infohash = self.client.torrents(sort="added_on", reverse=True)[0]["hash"]

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