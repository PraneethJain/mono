from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.widgets import (
    Static,
    Header,
    Footer,
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
    def __init__(self, card_data, id) -> None:
        super().__init__(id=id)
        self.card_data = card_data

    async def on_mount(self) -> None:
        cards = set(map(Card, self.card_data))
        highlighted_cards = {card for card in cards if card.has_class("highlight")}
        other_cards = cards - highlighted_cards
        for card in highlighted_cards:
            await self.mount(card)
        for card in other_cards:
            await self.mount(card)


class Switcher(Static):
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
        user_data = await ani.get_user_data()
        user_list_data = await ani.get_user_list(user_data["id"])
        card_data = [list["media"] for list in user_list_data]

        await self.mount(
            Horizontal(
                Button("Anime", id="anime"),
                Button("Profile", id="profile"),
                id="context-buttons",
            )
        )
        await self.mount(
            ContentSwitcher(
                Cards(card_data, id="anime"),
                Markdown("Profile Info", id="profile"),
                initial="anime",
            )
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one(ContentSwitcher).current = event.button.id

    async def on_quit(self) -> None:
        await gather(ani.close(), scraper.close())


class Mono(App):
    CSS_PATH = "style.css"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield Switcher()


if __name__ == "__main__":
    app = Mono()
    app.run()

# To do:
# 1. logging
