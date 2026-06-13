import asyncio
import xml.etree.ElementTree as ET
from pathlib import Path

import aiofiles
import aiohttp
import pluggy

from . import hookspecs
from .comicinfo import ComicInfo

pm = pluggy.PluginManager("komix")
pm.add_hookspecs(hookspecs)
pm.load_setuptools_entrypoints("komix")


async def read_comicinfo(xmlpath: Path) -> ComicInfo:
    async with aiofiles.open(xmlpath, "r") as f:
        xml = await f.read()
    root = ET.fromstring(xml)
    return ComicInfo(
        title=root.findtext("Title", default=""),
        id=root.findtext("ID", default=""),
        author=root.findtext("Author", default=""),
        summary=root.findtext("Summary", default=""),
        tags=root.findtext("Tags", default="").split(", "),
    )


async def _write_comicinfo(comicinfo: ComicInfo, xmlpath: Path):
    root = ET.Element("ComicInfo")
    ET.SubElement(root, "Title").text = comicinfo.title
    ET.SubElement(root, "ID").text = comicinfo.id
    ET.SubElement(root, "Author").text = comicinfo.author
    ET.SubElement(root, "Summary").text = comicinfo.summary
    ET.SubElement(root, "Tags").text = ", ".join(comicinfo.tags)
    async with aiofiles.open(xmlpath, "w") as f:
        await f.write(ET.tostring(root, encoding="utf-8"))


async def _download_cover(url: str, jpgpath: Path):
    async with aiofiles.open(jpgpath, "wb") as f:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                await f.write(await response.read())


async def scrape_by_dirname(dirpath: Path):
    comics = pm.hook.search(query=dirpath.name)
    if not comics:
        return

    comic0 = comics[0]
    comicinfo = pm.hook.fetch_comicinfo(comic_id=comic0.id)
    cover_url = pm.hook.fetch_cover_url(comic_id=comic0.id)
    await _write_comicinfo(comicinfo, dirpath / "ComicInfo.xml")
    await _download_cover(cover_url, dirpath / "cover.jpg")
