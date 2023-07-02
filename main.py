from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import (
    Header,
    Footer,
    LoadingIndicator,
    Markdown,
    ContentSwitcher,
    Button,
)

from asyncio import gather
from json import load, dump
from os import path

from anilist import ani
from card import Card
from info import data_path
from scrape import scraper


class Cards(VerticalScroll):
    def __init__(self, id) -> None:
        super().__init__(id=id)
        self.styles.height = "100%"
        self.loading_indicator = LoadingIndicator()
        self.call_later(self.fetch)

    async def fetch(self) -> None:
        user_list_data = await ani.get_user_list()
        user_list = [list["media"] for list in user_list_data]
        cards = set(map(Card, user_list))
        self.loading_indicator.display = False
        highlighted_cards = {card for card in cards if card.has_class("highlight")}
        other_cards = cards - highlighted_cards
        for card in highlighted_cards:
            await self.mount(card)
        for card in other_cards:
            await self.mount(card)

    def compose(self) -> ComposeResult:
        yield self.loading_indicator


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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Horizontal():
            yield Button("ok1", id="hello")
            yield Button("ok2", id="test")
        with ContentSwitcher(initial="hello"):
            yield Cards(id="hello")
            yield Markdown("Test", id="test")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one(ContentSwitcher).current = event.button.id

    async def on_quit(self) -> None:
        await gather(ani.close(), scraper.close())


if __name__ == "__main__":
    app = Mono()
    app.run()

# To do:
# 1. logging
