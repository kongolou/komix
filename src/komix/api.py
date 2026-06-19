from pathlib import Path

import aiofiles
import aiohttp
import pluggy
from kominfo import write_comic_info

from . import hookspecs

pm = pluggy.PluginManager("komix")
pm.add_hookspecs(hookspecs)
pm.load_setuptools_entrypoints("komix")


async def _download_cover(jpgpath: Path, url: str):
    async with aiofiles.open(jpgpath, "wb") as f:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                await f.write(await response.read())


async def scrape_by_dirname(dirpath: Path):
    results = pm.hook.scrape(title=dirpath.name)
    if not results:
        return
    result = results[0]
    comic_info, cover_url = result
    if not comic_info:
        return
    await write_comic_info(dirpath / "ComicInfo.xml", comic_info)
    if not cover_url:
        return
    await _download_cover(dirpath / "cover.jpg", cover_url)
