import requests
from bs4 import BeautifulSoup
from rich import print


def find_magnet(title: str):
    title = title.replace("2nd Season", "S2")
    search_term = " ".join(title.split()[:-2]) + " - " + f"{int(title.split()[-1]):02}"
    url = f"https://www.tokyotosho.info/rss.php?terms={search_term.replace(' ','+')}&type=1&searchName=true&searchComment=true&size_min=&size_max=&username="
    soup = BeautifulSoup(requests.get(url).text, "xml")
    options = {}
    for item in soup.find_all("item"):
        if item.category.text == "Anime":
            desc = BeautifulSoup(item.description.text)
            magnet = desc.find_all("a")[1]["href"]
            for line in desc.text.splitlines():
                if "Submitter" in line:
                    submitter = line.split()[-1]
                    break
            if submitter not in options:
                options[submitter] = {}
            if "1080p" in item.title.text:
                options[submitter]["1080p"] = magnet
            elif "720p" in item.title.text:
                options[submitter]["720p"] = magnet
            elif "480p" in item.title.text:
                options[submitter]["480p"] = magnet
            else:
                options[submitter]["noqp"] = magnet
    if "subsplease" in options:
        return options["subsplease"]["1080p"]
    elif "Erai-raws" in options:
        return options["Erai-raws"]["1080p"]