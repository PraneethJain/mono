import json
import os
import subprocess
import datetime
import configparser
from enum import Enum, auto

from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from rich.style import Style
from rich.styled import Styled
from rich.console import RenderableType
from rich.text import Text

from textual.app import App
from textual.geometry import clamp
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Header, Footer
from textual.views._grid_view import GridView

from anilist.query import get_user_list
from anilist.mutation import set_progress
from anilist.authenticate import get_token
from scraper import find_magnet
from downloader import Torrent
from appdata import AppDataPaths


class States(Enum):
    TO_AIR = auto()
    NEW_EPISODE = auto()
    DOWNLOADING_PAUSED = auto()
    DOWNLOADING_IN_PROGRESS = auto()
    DOWNLOADED = auto()
    COMPLETED = auto()


class Episode(Widget):

    renderable = Reactive(RenderableType)
    style = Reactive(Style())
    title = Reactive(Text())

    with open(r"./app/data/downloading.json", "r") as f:
        downloading = json.load(f)

    def __init__(
        self,
        media,
        ep_num,
        to_air: bool = False,
        name: str | None = None,
    ) -> None:

        super().__init__(name)

        self.series = media["title"]["romaji"].replace(":", "")
        self.ep_num = ep_num
        self.content = f"{self.series} - {self.ep_num:02}"
        self.media_id = media["id"]
        self.to_air = to_air
        if self.to_air:
            self.air_time = datetime.timedelta(
                seconds=media["nextAiringEpisode"]["timeUntilAiring"]
            )
            self.set_to_air()
        else:
            self.air_time = datetime.timedelta(seconds=0)
            if self.content in self.downloading:
                self.infohash = self.downloading[self.content]["infohash"]
                self.ep_title = self.downloading[self.content]["title"]
                if Torrent.is_completed(self.infohash):
                    self.set_downloaded()
                else:
                    self.paused = Torrent.get_torrent(self.infohash)["eta"] == 8640000
                    self.set_downloading()
            else:
                self.set_new_episode()

    def render(self) -> Panel:
        return Panel(
            self.renderable, style=self.style, title=self.title, title_align="left"
        )

    async def on_enter(self):
        self.style += Style(bgcolor="#232323")

    async def on_leave(self):
        self.style += Style(bgcolor="default")

    async def on_click(self, event) -> None:

        match self.state:

            case States.DOWNLOADED:
                if event.button == 1:
                    self.play(f"{Torrent.get_savepath(self.infohash)}\\{self.ep_title}")
                elif event.button == 3:
                    self.complete()

            case States.COMPLETED:
                self.uncomplete()
            case States.DOWNLOADING_IN_PROGRESS:
                self.pause()
            case States.DOWNLOADING_PAUSED:
                self.resume()
            case States.NEW_EPISODE:
                await self.download()

        with open(r"./app/data/downloading.json", "w") as f:
            json.dump(self.downloading, f)

    def set_to_air(self) -> None:

        self.state = States.TO_AIR

        self.to_air_right_style = Style(color="#F47068")
        self.to_air_left_style = Style(color="#FFB3AE")
        self.style = Style(color="#2a9d8f")
        self.title = Text("Releasing")
        self.update_to_air()

    def update_to_air(self, loop=True) -> None:
        self.renderable = Columns(
            [
                Align(f"{self.content}", align="left", style=self.to_air_left_style),
                Align(str(self.air_time), align="right", style=self.to_air_right_style),
            ],
            expand=True,
        )
        if self.air_time.total_seconds() < 2:
            self.set_new_episode()
        elif loop:
            self.air_time -= datetime.timedelta(seconds=1)
            self.set_timer(1, self.update_to_air)

    def set_new_episode(self) -> None:

        self.state = States.NEW_EPISODE

        self.title = Text("New Episode")
        self.renderable = Styled(self.content, Style(color="#42e2b8"))
        self.style = Style(color="#00b4d8")

    def set_downloading(self) -> None:

        self.state = States.DOWNLOADING_IN_PROGRESS

        self.downloading_left_style = Style(color="#F4A261")
        self.downloading_right_style = Style(color="#E76F51")
        self.style = Style(color="#219ebc")
        self.update_downloading()

    def update_downloading(self, loop=True) -> None:
        if Torrent.is_completed(self.infohash):
            self.set_downloaded()
        else:
            self.state = (
                States.DOWNLOADING_PAUSED
                if self.paused
                else States.DOWNLOADING_IN_PROGRESS
            )
            progress = clamp(Torrent.get_progress(self.infohash), 0, 100)
            self.title = Text(
                f"Downloading : {'Paused' if self.paused else 'In Progress'}"
            )
            self.renderable = Columns(
                [
                    Align(
                        f"{self.content}",
                        align="left",
                        style=self.downloading_left_style,
                    ),
                    Align(
                        f"{progress}%",
                        align="right",
                        style=self.downloading_right_style,
                    ),
                ],
                expand=True,
            )

            if loop:
                self.set_timer(1, self.update_downloading)

    def set_downloaded(self) -> None:

        self.state = States.DOWNLOADED

        self.title = Text("Downloaded")
        self.renderable = Styled(self.content, Style(color="#06d6a0"))
        self.style = Style(color="#0096c7")

    def set_completed(self) -> None:

        self.state = States.COMPLETED
        self.downloading.pop(self.content)
        self.renderable = Styled(self.content, Style(color="#42bfdd"))
        self.title = Text("Completed")
        self.style = Style(color="#48cae4")

    async def download(self) -> None:
        try:
            title, magnet = await find_magnet(self.content)
        except TypeError:
            self.renderable = Styled(
                f"{self.content} (Magnet not found!)", Style(color="#42e2b8")
            )
        else:
            series = " ".join(self.content.split()[:-2])
            self.torrent = Torrent(series, magnet)

            if self.content not in self.downloading:
                self.infohash = self.torrent.get_infohash()
                self.ep_title = title
                self.downloading[self.content] = {
                    "infohash": self.torrent.get_infohash(),
                    "title": title,
                }
                self.paused = False
                self.set_downloading()

    def pause(self) -> None:
        Torrent.pause_torrent(self.infohash)
        self.paused = True
        self.update_downloading(loop=False)

    def resume(self) -> None:
        Torrent.resume_torrent(self.infohash)
        self.paused = False
        self.update_downloading(loop=False)

    def complete(self) -> None:
        set_progress(self.media_id, self.ep_num)
        self.set_completed()

    def uncomplete(self) -> None:
        set_progress(self.media_id, self.ep_num - 1)
        self.downloading[self.content] = {
            "infohash": self.infohash,
            "title": self.ep_title,
        }
        self.set_downloaded()

    @staticmethod
    def play(path) -> None:
        subprocess.Popen(path, shell=True)


class Episodes(GridView):
    def on_mount(self) -> None:
        self.episodes = []
        for entry in get_user_list("CURRENT")["entries"]:
            new_episode = False
            current = entry["media"]["mediaListEntry"]["progress"]
            if entry["media"]["nextAiringEpisode"] is None:
                latest = entry["media"]["episodes"]
            else:
                latest = entry["media"]["nextAiringEpisode"]["episode"] - 1
            for i in range(current + 1, latest + 1):
                new_episode = True
                self.episodes.append(Episode(entry["media"], i))
            if not new_episode:
                self.episodes.append(Episode(entry["media"], latest + 1, True))

        self.episodes.sort(key=lambda episode: episode.air_time)

        self.grid.add_column("col")
        self.grid.add_row("row", size=3)
        self.grid.set_repeat(False, True)
        self.grid.place(*self.episodes)


class Mono(App):
    async def on_load(self, event) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event) -> None:
        self.header = Header(style="#FD7F20 on default")
        self.footer = Footer()
        self.episodes_view = Episodes()

        await self.view.dock(self.header, edge="top")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.episodes_view, edge="top")


if __name__ == "__main__":

    app_paths = AppDataPaths("mono")
    if app_paths.require_setup:
        app_paths.setup()
    config = configparser.ConfigParser()
    config.read(app_paths.config_path)
    if "access_token" not in config["DEFAULT"]:
        config["DEFAULT"]["access_token"] = get_token()
        with open(app_paths.config_path, "w") as config_file:
            config.write(config_file)
    os.environ["access_token"] = config["DEFAULT"]["access_token"]
    Mono.run(title="Mono", log=app_paths.log_file_path)
