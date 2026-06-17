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
    if not xml:
        return ComicInfo()
    root = ET.fromstring(xml)
    return ComicInfo(
        title=root.findtext("Title", default=""),
        id=root.findtext("Id", default=""),
        authors=root.findtext("Authors", default="").split(", "),
        summary=root.findtext("Summary", default=""),
        tags=root.findtext("Tags", default="").split(", "),
    )


async def _write_comicinfo(comicinfo: ComicInfo, xmlpath: Path):
    root = ET.Element("ComicInfo")
    ET.SubElement(root, "Title").text = comicinfo.title
    ET.SubElement(root, "Id").text = comicinfo.id
    ET.SubElement(root, "Authors").text = ", ".join(comicinfo.authors)
    ET.SubElement(root, "Summary").text = comicinfo.summary
    ET.SubElement(root, "Tags").text = ", ".join(comicinfo.tags)
    async with aiofiles.open(xmlpath, "w") as f:
        await f.write(ET.tostring(root, encoding="unicode"))


async def _download_cover(url: str, jpgpath: Path):
    async with aiofiles.open(jpgpath, "wb") as f:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                await f.write(await response.read())


async def scrape_by_dirname(dirpath: Path):
    s_results = pm.hook.search(query=dirpath.name)
    if not s_results:
        return
    comics = s_results[0]
    if not comics:
        return
    comic0_id = comics[0].id

    fc_results = pm.hook.fetch_comicinfo(comic_id=comic0_id)
    if fc_results:
        comicinfo = fc_results[0]
        await _write_comicinfo(comicinfo, dirpath / "ComicInfo.xml")

    fcu_results = pm.hook.fetch_cover_url(comic_id=comic0_id)
    if fcu_results:
        cover_url = fcu_results[0]
        await _download_cover(cover_url, dirpath / "cover.jpg")
