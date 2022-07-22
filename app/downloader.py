from qbittorrent import Client
from urllib3 import disable_warnings

disable_warnings(ResourceWarning)


class Torrent:

    client = Client("http://127.0.0.1:8080/")
    client.login("admin", "adminadmin")

    def __init__(self, series, magnet) -> None:
        self.series = series
        self.magnet = magnet
        self.download()

    def download(self) -> None:
        self.client.download_from_link(
            self.magnet,
            savepath=f"D:\\Torrents\\Anime\\{self.series}",
            category="Anime",
        )
        self.infohash = self.client.torrents(
            category="Anime", sort="added_on", reverse=True
        )[0]["hash"]

    def get_infohash(self) -> None:
        return self.infohash

    @classmethod
    def get_progress(cls, infohash) -> None:
        data = cls.client.get_torrent(infohash)
        return round(data["total_downloaded"] / data["total_size"] * 100, 2)

    @classmethod
    def pause_torrent(cls, infohash) -> None:
        cls.client.pause(infohash)

    @classmethod
    def resume_torrent(cls, infohash) -> None:
        cls.client.resume(infohash)

    @classmethod
    def is_completed(cls, infohash) -> None:
        return cls.client.get_torrent(infohash)["completion_date"] != -1

    @classmethod
    def get_savepath(cls, infohash) -> None:
        return cls.client.get_torrent(infohash)["save_path"]

    @classmethod
    def get_torrent(cls, infohash) -> None:
        return cls.client.get_torrent(infohash)
