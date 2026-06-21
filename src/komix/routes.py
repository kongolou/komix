from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse
from kominfo import ComicInfo, read_comic_info

from .api import scrape_by_dirname

STATIC_DIR = Path(__file__).parent / "static"

router = APIRouter()


@router.get("/")
async def get_root():
    idx = STATIC_DIR / "index.html"
    if not idx.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(idx, media_type="text/html")


@router.get("/favicon.ico")
async def get_favicon():
    ico = STATIC_DIR / "favicon.ico"
    if not ico.exists():
        raise HTTPException(status_code=404, detail="favicon.ico not found")
    return FileResponse(ico, media_type="image/x-icon")


@router.get("/api/comics", response_model=list[Path])
async def get_comics(rootdir: str = Query(None)):
    if not Path(rootdir).exists():
        raise HTTPException(status_code=404, detail="rootdir not found")
    return [dirpath for dirpath in Path(rootdir).iterdir() if dirpath.is_dir()]


@router.get("/api/comicinfo", response_model=ComicInfo)
async def get_comicinfo(dirpath: str = Query(None)):
    xmlpath = Path(dirpath) / "ComicInfo.xml"
    if not xmlpath.exists():
        raise HTTPException(status_code=404, detail="ComicInfo.xml not found")
    return await read_comic_info(xmlpath)


@router.get("/api/cover")
async def get_cover(dirpath: str = Query(None)):
    jpgpath = Path(dirpath) / "cover.jpg"
    if not jpgpath.exists():
        raise HTTPException(status_code=404, detail="cover.jpg not found")
    return FileResponse(jpgpath, media_type="image/jpeg")


@router.put("/api/scrape")
async def put_scrape(dirpath: str = Query(None)):
    await scrape_by_dirname(Path(dirpath))
    return Response(status_code=200)
