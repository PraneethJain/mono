import httpx
from bs4 import BeautifulSoup


async def find_magnet(search_term: str):
    search_term = search_term.replace("2nd Season", "S2")
    url = f"https://www.tokyotosho.info/rss.php?terms={search_term.replace(' ','+')}&type=1&searchName=true&searchComment=true&size_min=&size_max=&username="
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
    soup = BeautifulSoup(r.text, "xml")
    options = {}
    for item in soup.find_all("item"):
        if item.category.text == "Anime":
            desc = BeautifulSoup(item.description.text)
            magnet = desc.find_all("a")[1]["href"]
            title = item.title.text
            for line in desc.text.splitlines():
                if "Submitter" in line:
                    submitter = line.split()[-1]
                    break
            if submitter not in options:
                options[submitter] = {}
            if "1080p" in title:
                options[submitter]["1080p"] = title, magnet
            elif "720p" in title:
                options[submitter]["720p"] = title, magnet
            elif "480p" in title:
                options[submitter]["480p"] = title, magnet
            else:
                options[submitter]["noqp"] = title, magnet
    if "subsplease" in options:
        return options["subsplease"]["1080p"]
    elif "Erai-raws" in options:
        return options["Erai-raws"]["1080p"]
    else:
        temp = search_term.split()
        if len(temp) < 5:
            return None
        temp.pop(-3)
        search_term = " ".join(temp)
        return await find_magnet(search_term)
