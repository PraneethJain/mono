from rich.panel import Panel
from rich.style import Style

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, Placeholder
from textual.views._grid_view import GridView

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
        for ele in content:
            s += f"🟠 {ele}"
        return s

    def render(self) -> Panel:
        return Panel(self.string, style=self.style, title=self.title, padding=(1, 1))


class NewEpisode(Widget):
    
    mouse_over = Reactive(False)
    string = Reactive("Placeholder data")
    
    def __init__(
        self,
        content: str,
        title: str | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(name)
        self.content = content
        self.string = f"🔵 {self.content}"
        self.unhover = "#845EC2 on default"
        self.hover = "#D65DB1 on #FFC75F"
        self.title = title
        self.toggle = True
        
    def render(self) -> Panel:
        return Panel(self.string, style = self.hover if self.mouse_over else self.unhover, title=self.title)
    
    def on_enter(self):
        self.mouse_over = True
        
    def on_leave(self):
        self.mouse_over = False
        
    def on_click(self, event) -> None:
        self.toggle = not self.toggle
        self.string = f"🔵 {self.content}" if self.toggle else "🔴 You have been clicked"   
    


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
                self.new_episodes.append(
                    f"{entry['media']['title']['romaji']} Ep {i}\n"
                )

        await self.view.dock(self.header, edge="top")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.shows, edge="left", size=60)
        await self.view.dock(*(NewEpisode(ele) for ele in self.new_episodes), edge="top", size=3)


Mono.run(title="Mono", log="textual.log")
