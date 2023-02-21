import httpx
from bs4 import BeautifulSoup

import asyncio
from rich import print


class Scraper:
    url = "https://nyaa.si/?f=2&c=1_2&q="

    def __init__(self) -> None:
        self.client = httpx.AsyncClient()

    async def find_magnets(self, search_term: str) -> str:
        url = self.url + search_term.replace(" ", "+")
        r = await self.client.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        
        for i, row in enumerate(soup.select(".success")):
            if i==0:
                print(row)
                print()
            try:
                title = (
                    row.find(True)
                    .find_next_sibling()
                    .find(True)
                    .find_next_sibling()
                    .attrs["title"]
                )
                magnet = (
                    row.find(True)
                    .find_next_sibling()
                    .find_next_sibling()
                    .find(True)
                    .find_next_sibling()
                    .attrs["href"]
                )
            except:
                print(row)
                print()

        return (title, magnet)

    async def close(self) -> None:
        await self.client.aclose()

async def main():
    scraper = Scraper()
    scraper.find_magnets("Otonari no Tenshi-sama ni Itsunomanika Dame Ningen ni Sareteita Ken - 01")