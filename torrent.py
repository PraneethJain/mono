from qbittorrent import Client
from info import data_path
from json import load


class Torrent:
    client = Client("http://127.0.0.1:8080/")
    client.login("admin", "adminadmin")

    def __init__(self, series: str, magnet: str) -> None:
        self.series = series
        self.magnet = magnet
        with open(data_path, "r") as f:
            data = load(f)

        self.download_path = f"{data['download_path']}\\{series}"
        self.client.download_from_link(self.magnet, savepath=self.download_path)
        self.infohash = self.client.torrents(sort="added_on", reverse=True)[0]["hash"]

    @classmethod
    def get_download_percentage(cls, infohash) -> float:
        data = cls.client.get_torrent(infohash)
        return round(data["total_downloaded"] / data["total_size"] * 100, 1)

    @classmethod
    def is_completed(cls, infohash) -> bool:
        return cls.client.get_torrent(infohash)["completion_date"] != -1
