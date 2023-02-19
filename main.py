from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, Markdown, Button
from textual.containers import Container, Horizontal

import anilist


class ProgressSetter(Static):
    def __init__(self, progress: int) -> None:
        super().__init__()
        self.progress = progress
        self.minus = Button("-")
        self.plus = Button("+")
        self.middle = Button(str(self.progress))

    def compose(self) -> ComposeResult:
        yield Container(self.minus, self.middle, self.plus)


class AnimeCard(Static):
    def __init__(self, info: dict) -> None:
        super().__init__()
        self.info = info
        self.active = False
        self.episodes_to_watch = list(
            range(
                self.info["mediaListEntry"]["progress"] + 1,
                self.info["nextAiringEpisode"]["episode"],
            )
        )
        self.title_widget = Static(self.info["title"]["romaji"])
        self.description_widget = Markdown(self.info["description"], id="description")
        self.progress_widget = ProgressSetter(self.info["mediaListEntry"]["progress"])

    def compose(self) -> ComposeResult:
        yield Container(
            self.title_widget,
            self.progress_widget,
            self.description_widget,
        )

    def on_click(self) -> None:
        if self.active:
            self.styles.animate("height", value=1, final_value=10, duration=0.15)
            self.remove_class("active")
        else:
            self.styles.animate("height", value=10, final_value=1, duration=0.15)
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
        user_list_data = await anilist.get_user_list()
        user_list = [l["media"] for l in user_list_data]
        self.mount(Main(user_list))


if __name__ == "__main__":
    app = Mono()
    app.run()
