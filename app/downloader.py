from qbittorrent import Client
from rich import print
from scraper import find_magnet

class Torrent:

    def __init__(self, series, magnet) -> None:
        self.series = series
        self.magnet = magnet
        self.client = Client("http://127.0.0.1:8080/")
        self.client.login("admin", "adminadmin")
        self.download()
        
    def download(self) -> None:
        self.client.download_from_link(self.magnet, savepath=f"D:\\Torrents\\Anime\\{self.series}", category="Anime")
        self.infohash = self.client.torrents(category="Anime", sort="added_on", reverse=True)[0]["hash"]
        self.data = self.client.get_torrent(self.infohash)
        
    def get_progress(self) -> None:
        return round(self.data['total_downloaded']/self.data['total_size']*100,2)
