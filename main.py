from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, Markdown, TextLog, Button
from textual.containers import Container, Horizontal

import sys
import os
import asyncio

import anilist


temp = {
    "id": 138565,
    "title": {
        "romaji": "Fumetsu no Anata e Season 2",
        "english": "To Your Eternity Season 2",
        "native": "不滅のあなたへ Season 2",
        "userPreferred": "Fumetsu no Anata e Season 2",
    },
    "format": "TV",
    "status": "RELEASING",
    "description": """After seeing enough death and tragedy, the immortal Fushi secludes himself on an island,
defending himself from enemy Nokkers. However, instead of attacking Fushi in isolation, Nokkers begin targeting the 
settlements outside of his reach in hopes of luring him out. Soon, a group known as the Guardians—led by Hisame, the
descendant of the deceased warrior Hayase—finds Fushi.\n<br><br>\nInspired by how Fushi protected Janada Island from
the Nokkers years ago, the Guardians have grown a considerable following and are recognized throughout the world.   
Initially reluctant, Fushi allows the Guardians to accompany him to the site of the Nokkers' recent attack. In their
village, Fushi meets a few valuable allies, both new and old. But as the conflict with the Nokkers only leads to    
more loss, Fushi must find the inner strength to face his inevitable sorrow.\n<br><br>\n(Source: MAL Rewrite)""",
    "startDate": {"day": 23, "month": 10, "year": 2022},
    "endDate": {"day": None, "month": None, "year": None},
    "season": "FALL",
    "seasonYear": 2022,
    "episodes": 20,
    "duration": 25,
    "source": "MANGA",
    "mediaListEntry": {"progress": 13},
    "nextAiringEpisode": {
        "airingAt": 1676800800,
        "timeUntilAiring": 88537,
        "episode": 17,
    },
}


class Buttons(Static):
    def __init__(self, episodes: list[int]) -> None:
        super().__init__()
        self.episodes = episodes
        self.buttons = [Button(str(ep)) for ep in self.episodes]

    def compose(self) -> ComposeResult:
        yield Horizontal(*self.buttons)


class AnimeCard(Static):
    def __init__(self, info: dict) -> None:
        super().__init__()
        self.info = info
        self.text_log = TextLog()
        self.active = False
        self.episodes_to_watch = list(
            range(
                self.info["mediaListEntry"]["progress"] + 1,
                self.info["nextAiringEpisode"]["episode"],
            )
        )

        self.title_widget = Static(self.info["title"]["romaji"])
        self.description_widget = Markdown(self.info["description"], id="description")
        self.buttons_widget = Buttons(self.episodes_to_watch)

    def compose(self) -> ComposeResult:
        yield Container(
            self.title_widget,
            self.buttons_widget,
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
    def compose(self) -> ComposeResult:
        for ele in medias:
            yield AnimeCard(ele)


class Mono(App):

    CSS_PATH = "style.css"
    BINDINGS = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.mount(Header(True))
        self.mount(Footer())
        self.mount(Main())


if __name__ == "__main__":
    medias = [l["media"] for l in asyncio.run(anilist.get_user_list())]
    app = Mono()
    app.run()
