from anilist import ani
import asyncio
from rich import print


async def main():
    print(await ani.get_user_list())
    await ani.close()


if __name__ == "__main__":
    asyncio.run(main())
