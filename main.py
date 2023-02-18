import anilist
import asyncio
from rich import print

if __name__ == "__main__":
    print(asyncio.run(anilist.get_user_list()))
