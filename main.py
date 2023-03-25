from textual.app import App, ComposeResult
from textual.widgets import (
    Static,
    Header,
    Footer,
    ContentSwitcher,
    Markdown,
    LoadingIndicator,
    Placeholder,
)
from textual.reactive import reactive

from asyncio import gather
from json import load, dump
from os import path

from anilist import ani
from card import Card
from info import data_path
from scrape import scraper


class Mono(Static):
    def __init__(self) -> None:
        super().__init__()
        self.loading_indicator = LoadingIndicator()
        self.cards = []
        self.call_later(self.fetch)

    async def fetch(self) -> None:
        user_list_data = await ani.get_user_list()
        user_list = [l["media"] for l in user_list_data]
        self.cards = list(map(Card, user_list))
        self.loading_indicator.display = False
        for card in self.cards:
            await self.mount(card)

    def compose(self) -> ComposeResult:
        yield self.loading_indicator


class Main(App):
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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield Mono()

    async def on_quit(self) -> None:
        await gather(ani.close(), scraper.close())


if __name__ == "__main__":
    app = Main()
    app.run()

# To do:
# 1. logging
