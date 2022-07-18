from rich.markdown import Markdown
from rich.panel import Panel
from rich.style import Style
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, ScrollView, Placeholder, Static

from anilist.query import get_user_list


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
        for i, ele in enumerate(content, start=1):
            s += f"🟠 {ele}"
        return s

    def render(self) -> Panel:
        return Panel(self.string, style=self.style, title=self.title, padding=(1, 1))


class Mono(App):
    async def on_load(self, event) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event) -> None:
        self.header = Header(style="#FD7F20 on default")
        self.footer = Footer()
        self.shows = PanelList(
            [
                entry["media"]["title"]["romaji"] + "\n"
                for entry in get_user_list("CURRENT")["entries"]
            ],
            style="#FDB750 on default",
            title="[bold red]Currently Watching Shows",
        )
        await self.view.dock(self.header, edge="top")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.shows, edge="left", size=60)
        await self.view.dock(Placeholder(), Placeholder(), edge="top")


Mono.run(title="Mono", log="textual.log")
