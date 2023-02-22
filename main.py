from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, Markdown, Button
from textual.containers import Container
from textual.geometry import clamp

from enum import Enum, auto
from asyncio import gather
from os import path, makedirs
from json import load, dump
from subprocess import Popen

from anilist import ani
from scrape import scraper
from torrent import Torrent
from info import data_path, cache_dir, cache_path


class ProgressState(Enum):
    next_episode_unavailable = auto()
    next_episode_available = auto()
    finding_torrent = auto()
    downloading = auto()
    downloaded = auto()


class ProgressSetter(Static):

    if not path.exists(cache_dir):
        makedirs(cache_dir)
    if not path.exists(cache_path):
        with open(cache_path, "w") as f:
            dump({}, f)

    with open(cache_path, "r") as f:
        downloads: dict[str, list[str, str]] = load(f)

    def __init__(
        self, progress: int, max_progress: int, media_id: int, titles: dict[str, str]
    ) -> None:
        super().__init__()

        self.progress = progress
        self.max_progress = max_progress
        self.media_id = media_id
        self.titles = titles
        self.title = self.titles["romaji"]
        self.minus_button = Button("-", self.progress == 0, id="minus")
        self.plus_button = Button("+", self.progress == self.max_progress, id="plus")
        self.middle_button = Button(str(self.progress), True, id="middle")
        self.state_button = Button(f"Loading", id="state")
        self.set_state()

    def set_state(self) -> None:

        if self.progress == self.max_progress:
            self.set_next_episode_unavailable()
        else:

            if (key := f"{self.title} - {self.progress + 1}") in self.downloads:
                infohash, filename = self.downloads[key]
                self.torrent = Torrent(self.title, infohash=infohash)
                self.torrent_filename = filename
                self.state_button.disabled = True
                self.plus_button.disabled = True
                self.minus_button.disabled = True

                if self.torrent.is_completed():
                    self.set_downloaded(stop_timer=False)
                else:
                    self.set_downloading()

            else:
                self.set_next_episode_available()

    def set_next_episode_unavailable(self) -> None:
        self.state = ProgressState.next_episode_unavailable
        self.state_button.display = False

    def set_next_episode_available(self) -> None:
        self.state = ProgressState.next_episode_available

        self.state_button.label = f"⬇️ {self.progress + 1}"

    def set_downloading(self) -> None:
        self.state = ProgressState.downloading

        self.download_timer = self.set_interval(1, self.download)

    def set_downloaded(self, stop_timer=True) -> None:
        self.state = ProgressState.downloaded
        if stop_timer:
            self.download_timer.stop_no_wait()
        self.state_button.label = f"▶️ {self.progress + 1}"
        self.state_button.disabled = False
        self.plus_button.disabled = False
        self.minus_button.disabled = False

    def compose(self) -> ComposeResult:
        yield Container(self.minus_button, self.middle_button, self.plus_button)
        yield self.state_button

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "minus":
                self.progress = max(0, self.progress - 1)
                await self.update_progress()
            case "plus":
                self.progress = min(self.max_progress, self.progress + 1)
                await self.update_progress()
            case "state":
                match self.state:
                    case ProgressState.next_episode_available:
                        self.state = ProgressState.finding_torrent
                        self.state_button.disabled = True
                        self.plus_button.disabled = True
                        self.minus_button.disabled = True
                        self.state_button.label = f"↺ Finding torrent"

                        self.magnets = await scraper.find_magnets(
                            self.title, self.progress + 1
                        )
                        self.torrent = Torrent(
                            self.title, magnet=self.magnets["first"][1]
                        )
                        self.torrent_filename = self.magnets["first"][0]
                        self.downloads[f"{self.title} - {self.progress + 1}"] = [
                            self.torrent.infohash,
                            self.torrent_filename,
                        ]
                        with open(cache_path, "w") as f:
                            dump(self.downloads, f)

                        self.set_downloading()

                    case ProgressState.downloaded:
                        Popen(
                            f"{self.torrent.download_path}\\{self.torrent_filename}",
                            shell=True,
                        )

    async def update_progress(self) -> None:
        await ani.set_progress(self.media_id, self.progress)

        self.middle_button.label = str(self.progress)
        self.minus_button.disabled = self.progress == 0
        self.plus_button.disabled = self.progress == self.max_progress

        self.set_state()

    def download(self) -> None:
        self.state_button.label = (
            f"{clamp(self.torrent.get_download_percentage(), 0.0, 100.0):.2f} %"
        )
        if self.torrent.is_completed():
            self.set_downloaded()


class AnimeCard(Static):
    def __init__(self, info: dict) -> None:
        super().__init__()
        self.info = info
        self.active = False
        self.title_widget = Static(self.info["title"]["romaji"])
        self.progress = self.info["mediaListEntry"]["progress"]
        if self.info["status"] == "FINISHED":
            self.max_progress = self.info["episodes"]
        elif self.info["nextAiringEpisode"] is None:
            self.max_progress = self.progress
        else:
            self.max_progress = self.info["nextAiringEpisode"]["episode"] - 1

        self.progress_widget = ProgressSetter(
            self.progress, self.max_progress, self.info["id"], self.info["title"]
        )
        self.description_widget = Markdown(self.info["description"], id="description")

    def compose(self) -> ComposeResult:
        yield Container(
            self.title_widget,
            self.progress_widget,
            self.description_widget,
        )

    def on_click(self) -> None:
        if self.active:
            self.styles.animate("height", value=1, final_value=15, duration=0.15)
            self.remove_class("active")
        else:
            self.styles.animate("height", value=15, final_value=1, duration=0.15)
            self.add_class("active")

        self.active = not self.active


class Main(Static):
    def __init__(self, user_list: list[dict]):
        super().__init__()
        self.user_list = user_list

    def compose(self) -> ComposeResult:
        for ele in self.user_list:
            yield AnimeCard(ele)


class Mono(App):

    CSS_PATH = "style.css"
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        ani.get_token()

        with open(data_path, "r") as f:
            data = load(f)
            if "download_path" not in data:
                download_path = ""
                while not path.exists(download_path):
                    download_path = input("Enter path to store downloads: ")
                data["download_path"] = download_path
        with open(data_path, "w") as f:
            dump(data, f)

    async def on_mount(self) -> None:
        self.mount(Header(True))
        self.mount(Footer())
        user_list_data = await ani.get_user_list()
        user_list = [l["media"] for l in user_list_data]
        self.mount(Main(user_list))

    async def on_quit(self) -> None:
        await gather(ani.close(), scraper.close())


if __name__ == "__main__":
    app = Mono()
    app.run()
