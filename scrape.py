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
        found_first = False
        for node in soup.select(".success"):
            title = node.select("td")[1].select("a")[-1].attrs["title"]
            magnet = node.select("td")[2].select("a")[-1].attrs["href"]
            magnets[title] = magnet
            if (
                all(
                    keyword in title
                    for keyword in ["[SubsPlease]", "1080p", f" {episode_number:02d} "]
                )
                and not found_first
            ):
                magnets["first"] = (title, magnet)
                found_first = True

        return magnets

    async def close(self) -> None:
        await self.client.aclose()


scraper = Scraper()


# async def main():
#     scraper = Scraper()
#     series = "Otonari no Tenshi-sama ni Itsunomanika Dame Ningen ni Sareteita Ken"
#     print(await scraper.find_magnets(series, 8))
#     await scraper.close()


# if __name__ == "__main__":
#     asyncio.run(main())
