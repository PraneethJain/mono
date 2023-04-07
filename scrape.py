import httpx
from bs4 import BeautifulSoup
from edge_cases import mappings

# import asyncio
# from rich import print


class Scraper:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient()

    async def find_magnet(self, series: str, episode_number: int) -> str:
        if series in mappings:
            episode_number += mappings[series][1]
            series = mappings[series][0]
        elif "Season " in series:
            series = series.replace("Season ", "S")
        search_term = f"{series} - {episode_number:02d} 1080p"
        url = f'https://tokyotosho.org/search.php?terms={search_term.replace(" ", "+")}&type=1&searchName=true&username=subsplease'

        r = await self.client.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        for node in soup.select(".sprite_magnet"):
            episode_data = node.parent.parent.select("a")
            magnet = episode_data[0].attrs["href"]
            title = episode_data[1].text
            title = title[:-4] + title[-3:]

            if f" {episode_number:02d} " in title:
                return (title, magnet)

        return None

    async def close(self) -> None:
        await self.client.aclose()


scraper = Scraper()


# async def main():
# scraper = Scraper()
# series = "Dr. STONE: NEW WORLD"
# print(await scraper.find_magnet(series, 1))
# await scraper.close()


# if __name__ == "__main__":
# asyncio.run(main())
