from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, Markdown, Button
from textual.containers import Container
from enum import Enum, auto

from anilist import ani


class ProgressState(Enum):
    next_episode_unavailable = auto()
    next_episode_available = auto()
    finding_torrent = auto()
    downloading = auto()
    downloaded = auto()


class ProgressSetter(Static):
    def __init__(
        self, progress: int, max_progress: int, media_id: int, titles: dict[str, str]
    ) -> None:
        super().__init__()

        self.progress = progress
        self.max_progress = max_progress
        self.media_id = media_id
        self.titles = titles
        self.minus_button = Button("-", self.progress == 0, id="minus")
        self.plus_button = Button("+", self.progress == self.max_progress, id="plus")
        self.middle_button = Button(str(self.progress), True, id="middle")

        self.state = ProgressState.next_episode_unavailable
        if self.progress != self.max_progress:
            self.state = ProgressState.next_episode_available

        # To do:
        # Condition to check if next episode is downloading/ready to watch and set state

        self.state_button = Button(f"⬇️ {self.progress + 1}", id="state")

    def compose(self) -> ComposeResult:
        yield Container(self.minus_button, self.middle_button, self.plus_button)

        if self.state != ProgressState.next_episode_unavailable:
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
                        # Find the torrent link and switch the state to downloading
                        # Use self.set_timer() to check downloading percentage

                    case ProgressState.downloaded:
                        self.state_button.disabled = True
                        # Open subprocess to play the downloaded file

    async def update_progress(self) -> None:
        await ani.set_progress(self.media_id, self.progress)

        self.middle_button.label = str(self.progress)
        self.minus_button.disabled = self.progress == 0
        self.plus_button.disabled = self.progress == self.max_progress


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

    async def on_mount(self) -> None:
        self.mount(Header(True))
        self.mount(Footer())
        user_list_data = await ani.get_user_list()
        user_list = [l["media"] for l in user_list_data]
        self.mount(Main(user_list))

    async def on_quit(self) -> None:
        await ani.close()


if __name__ == "__main__":
    app = Mono()
    app.run()
