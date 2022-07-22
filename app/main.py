import json
import os

from rich.panel import Panel
from rich.style import Style

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, Placeholder

from anilist.query import get_user_list
from anilist.mutation import set_progress
from scraper import find_magnet
from downloader import Torrent


class PanelList(Widget):
    def __init__(
        self,
        content: list,
        style: Style = "none",
        title: str | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(name)
        self.string = self.process(content)
        self.style = style
        self.title = title

    def process(self, content):
        s = ""
        for ele in content:
            s += f"🟠 {ele}"
        return s

    def render(self) -> Panel:
        return Panel(self.string, style=self.style, title=self.title, padding=(1, 1))


class Episode(Widget):

    string = Reactive("")
    style = Reactive("none")
    title = Reactive("none")

    with open(r"./app/data/downloading.json", "r") as f:
        downloading = json.load(f)

    def __init__(
        self,
        media,
        ep_num,
        name: str | None = None,
    ) -> None:

        super().__init__(name)

        self.content = f"{media['title']['romaji']} Ep {ep_num}".replace(':','')
        self.ep_num = ep_num
        self.media_id = media["id"]
        self.string = f"🔵 {self.content}"
        self.unhover = "#845EC2 on default"
        self.hover = "#D65DB1 on #FFC75F"
        self.style = self.unhover
        if self.content in self.downloading:
            if Torrent.is_completed(self.downloading[self.content]["infohash"]):
                self.string = f"🟢 {self.content}"
                self.title = "Downloaded"
            else:
                self.string = f"🟠 {self.content}"
                self.set_interval(1, self.progress)
                self.paused = (
                    Torrent.get_torrent(self.downloading[self.content]["infohash"])[
                        "eta"
                    ]
                    == 8640000
                )
                self.title = (
                    "Downloading : Paused"
                    if self.paused
                    else "Downloading : In Progress"
                )
        else:
            self.title = "New Episode"
            self.string = f"🔵 {self.content}"

    def render(self) -> Panel:
        return Panel(
            self.string, style=self.style, title=self.title, title_align="left"
        )

    def on_enter(self):
        self.style = self.hover

    def on_leave(self):
        self.style = self.unhover

    def on_click(self, event) -> None:

        if self.title == "Downloaded":

            if event.button == 1:
                self.title = "Now Playing"
                os.system(
                    f"\"{Torrent.get_savepath(self.downloading[self.content]['infohash'])}\\{self.downloading[self.content]['title']}\""
                )
                self.title = "Downloaded"
            elif event.button == 3:
                set_progress(self.media_id, self.ep_num)
                self.string = f"🟡 {self.content}"
                self.title = "Completed"
        elif self.title == "Completed":
            if event.button == 3:
                set_progress(self.media_id, self.ep_num - 1)
                self.title = "Downloaded"
                self.string = f"🟢 {self.content}"

        elif "Downloading" in self.title:
            if self.paused:
                self.title = "Downloading : In Progress"
                Torrent.resume_torrent(self.downloading[self.content]["infohash"])
            else:
                self.title = "Downloading : Paused"
                Torrent.pause_torrent(self.downloading[self.content]["infohash"])
            self.paused = not self.paused

        elif self.title == "New Episode":
            title, magnet = find_magnet(self.content)
            series = " ".join(self.content.split()[:-2])
            self.torrent = Torrent(series, magnet)
            if self.content not in self.downloading:
                self.downloading[self.content] = {
                    "infohash": self.torrent.get_infohash(),
                    "title": title,
                }
                self.title = "Downloading : In Progress"
                self.paused = False
                self.set_interval(1, self.progress)

            self.string = f"🟠 {self.content}"

        with open(r"./app/data/downloading.json", "w") as f:
            json.dump(self.downloading, f)

    def progress(self) -> None:
        if Torrent.is_completed(self.downloading[self.content]["infohash"]):
            if self.title != "Completed":
                self.title = "Downloaded"
                self.string = f"🟢 {self.content}"
        else:
            progress = Torrent.get_progress(self.downloading[self.content]["infohash"])
            if progress > 100:
                progress = 100
            else:
                self.string = (
                    f"{'⚪' if self.paused else '🟠'  } {self.content} {progress}"
                )


class Mono(App):
    async def on_load(self, event) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event) -> None:
        self.header = Header(style="#FD7F20 on default")
        self.footer = Footer()
        self.user_list = get_user_list("CURRENT")["entries"]
        self.shows = PanelList(
            [entry["media"]["title"]["romaji"] + "\n" for entry in self.user_list],
            style="#FDB750 on default",
            title="[bold red]Currently Watching Shows",
        )

        self.new_episodes = []
        for entry in self.user_list:
            current = entry["media"]["mediaListEntry"]["progress"]
            if entry["media"]["nextAiringEpisode"] is None:
                latest = entry["media"]["episodes"]
            else:
                latest = entry["media"]["nextAiringEpisode"]["episode"] - 1
            for i in range(current + 1, latest + 1):
                self.new_episodes.append((entry["media"], i))
                # self.new_episodes.append(f"{entry['media']['title']['romaji']} Ep {i}")

        await self.view.dock(self.header, edge="top")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.shows, edge="left", size=50)
        await self.view.dock(
            *(Episode(*ele) for ele in self.new_episodes), edge="top", size=3
        )


Mono.run(title="Mono", log="textual.log")
