from requests import get
from bs4 import BeautifulSoup


def find_magnet(title: str):
    title = title.replace("2nd Season", "S2")
    search_term = " ".join(title.split()[:-2]) + " - " + f"{int(title.split()[-1]):02}"
    url = f"https://www.tokyotosho.info/rss.php?terms={search_term.replace(' ','+')}&type=1&searchName=true&searchComment=true&size_min=&size_max=&username="
    soup = BeautifulSoup(get(url).text, "xml")
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
        temp = title.split()
        if len(temp) < 5:
            return None
        temp.pop(-3)
        title = " ".join(temp)
        return find_magnet(title)
