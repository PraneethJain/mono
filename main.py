from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, Markdown, Button
from textual.containers import Container

from anilist import ani


class ProgressSetter(Static):
    def __init__(self, progress: int, max_progress: int, media_id: int) -> None:
        super().__init__()

        self.media_id = media_id
        self.progress = progress
        self.max_progress = max_progress
        self.minus = Button("-", self.progress == 0, id="minus")
        self.plus = Button("+", self.progress == self.max_progress, id="plus")
        self.middle = Button(str(self.progress), True, id="middle")

        self.next_episode_available = self.progress != self.max_progress
        self.download_button = Button(f"⬇️ {self.progress + 1}", id="download")

    def compose(self) -> ComposeResult:
        yield Container(self.minus, self.middle, self.plus)
        if self.next_episode_available:
            yield self.download_button

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "minus":
                self.progress = max(0, self.progress - 1)
                await self.update_progress()
            case "plus":
                self.progress = min(self.max_progress, self.progress + 1)
                await self.update_progress()
            case "download":
                pass

    async def update_progress(self) -> None:
        await ani.set_progress(self.media_id, self.progress)

        self.middle.label = str(self.progress)
        self.minus.disabled = self.progress == 0
        self.plus.disabled = self.progress == self.max_progress


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
            self.progress, self.max_progress, self.info["id"]
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
