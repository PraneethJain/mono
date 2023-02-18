import anilist
import asyncio
import rich

rich.print(asyncio.run(anilist.get_user_list()))
