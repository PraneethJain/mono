import httpx
from bs4 import BeautifulSoup
from edge_cases import mappings

# import asyncio
# from rich import print


class Scraper:
    url = "https://nyaa.si/?f=2&c=1_2&q="

    def __init__(self) -> None:
        self.client = httpx.AsyncClient()

    async def find_magnets(self, series: str, episode_number: int) -> str:
        if series in mappings:
            episode_number += mappings[series][1]
            series = mappings[series][0]
        elif "Season " in series:
            series = series.replace("Season ", "S")
        search_term = f"{series} - {episode_number:02d}"
        url = self.url + search_term.replace(" ", "+")
        r = await self.client.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        magnets = {}
        for node in soup.select(".success"):
            title = node.select("td")[1].select("a")[-1].attrs["title"]
            magnet = node.select("td")[2].select("a")[-1].attrs["href"]
            magnets[title] = magnet
            if "[SubsPlease]" in title and "1080p" in title:
                magnets["first"] = (title, magnet)

        return magnets

    async def close(self) -> None:
        await self.client.aclose()


scraper = Scraper()

# async def main():
#     scraper = Scraper()
#     series = "Fumetsu no Anata e Season 2"
#     print(await scraper.find_magnets(series, 7))
#     await scraper.close()


# if __name__ == "__main__":
#     asyncio.run(main())
