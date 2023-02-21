from anilist import ani
import asyncio
from rich import print


async def main():
    print(await ani.get_user_list())
    print(await ani.set_progress(142838, 0))
    await ani.close()


if __name__ == "__main__":
    asyncio.run(main())
