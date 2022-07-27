import json
import subprocess
import datetime

from rich.panel import Panel
from rich.style import Style

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Header, Footer
from textual.views._grid_view import GridView

from anilist.query import get_user_list
from anilist.mutation import set_progress
from scraper import find_magnet
from downloader import Torrent


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
        to_air: bool = False,
        name: str | None = None,
    ) -> None:

        super().__init__(name)

        self.content = f"{media['title']['romaji']} Ep {ep_num}".replace(":", "")
        self.ep_num = ep_num
        self.media_id = media["id"]
        self.style = "none"
        self.to_air = to_air
        if self.to_air:
            self.air_time = datetime.timedelta(
                seconds=media["nextAiringEpisode"]["timeUntilAiring"]
            )
            self.set_to_air()
        else:
            self.air_time = datetime.timedelta(seconds=0)
            if self.content in self.downloading:
                if Torrent.is_completed(self.downloading[self.content]["infohash"]):
                    self.set_downloaded()
                else:
                    self.paused = (
                        Torrent.get_torrent(self.downloading[self.content]["infohash"])[
                            "eta"
                        ]
                        == 8640000
                    )
                    self.set_downloading()
            else:
                self.set_new_episode()

    def render(self) -> Panel:
        return Panel(
            self.string, style=self.style, title=self.title, title_align="left"
        )

    def on_enter(self):
        pass

    def on_leave(self):
        pass

    def on_click(self, event) -> None:

        if self.title == "Downloaded":
            if event.button == 1:
                self.play(
                    f"{Torrent.get_savepath(self.downloading[self.content]['infohash'])}\\{self.downloading[self.content]['title']}"
                )
            elif event.button == 3:
                self.complete()

        elif self.title == "Completed":
            self.uncomplete()

        elif "Downloading" in self.title:
            self.pause_resume()

        elif self.title == "New Episode":
            self.download()

        with open(r"./app/data/downloading.json", "w") as f:
            json.dump(self.downloading, f)

    def set_to_air(self) -> None:
        self.title = "Releasing"
        if width := self.size.width:
            self.string = f"🟣 {self.content} {' '*(width-len(str(self.air_time))-len(self.content)-10)} {self.air_time}"
            self.air_time -= datetime.timedelta(seconds=1)
        else:
            self.string = f"🟣 {self.content}"
        self.set_timer(1, self.set_to_air)

    def set_new_episode(self) -> None:
        self.title = "New Episode"
        self.string = f"🔵 {self.content}"

    def set_downloading(self) -> None:
        if Torrent.is_completed(self.downloading[self.content]["infohash"]):
            if self.title != "Completed":
                self.set_downloaded()
        else:

            progress = Torrent.get_progress(self.downloading[self.content]["infohash"])
            if progress > 100:
                progress = 100

            self.set_timer(1, self.set_downloading)

            if self.paused:
                self.title = "Downloading : Paused"
                self.string = f"⚪ {self.content} {progress}%"
            else:
                self.title = "Downloading : In Progress"
                self.string = f"🟠 {self.content} {progress}%"

    def set_downloaded(self) -> None:
        self.title = "Downloaded"
        self.string = f"🟢 {self.content}"

    def set_completed(self) -> None:
        self.string = f"🟡 {self.content}"
        self.title = "Completed"

    def download(self) -> None:
        title, magnet = find_magnet(self.content)
        series = " ".join(self.content.split()[:-2])
        self.torrent = Torrent(series, magnet)

        if self.content not in self.downloading:
            self.downloading[self.content] = {
                "infohash": self.torrent.get_infohash(),
                "title": title,
            }
            self.paused = False
            self.set_downloading()

    def pause_resume(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.title = "Downloading : Paused"
            Torrent.pause_torrent(self.downloading[self.content]["infohash"])
        else:
            self.title = "Downloading : In Progress"
            Torrent.resume_torrent(self.downloading[self.content]["infohash"])

    def complete(self) -> None:
        set_progress(self.media_id, self.ep_num)
        self.set_completed()

    def uncomplete(self) -> None:
        set_progress(self.media_id, self.ep_num - 1)
        self.set_downloaded()

    @staticmethod
    def play(path) -> None:
        subprocess.Popen(path, shell=True)


class Episodes(GridView):
    def __init__(self, user_list, layout=None, name: str | None = None) -> None:
        super().__init__(layout, name)
        self.user_list = user_list

    def on_mount(self) -> None:
        self.episodes = []
        for entry in self.user_list:
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
        self.grid.add_row("row", repeat=len(self.episodes) + 1, size=3)
        self.grid.place(*self.episodes)


class Mono(App):
    async def on_load(self, event) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event) -> None:
        self.header = Header(style="#FD7F20 on default")
        self.footer = Footer()
        self.user_list = get_user_list("CURRENT")["entries"]
        self.episodes_view = Episodes(self.user_list)

        await self.view.dock(self.header, edge="top")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.episodes_view, edge="top")


Mono.run(title="Mono", log="textual.log")
