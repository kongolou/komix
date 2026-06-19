import pluggy

hookspec = pluggy.HookspecMarker("komix")


@hookspec
def scrape(title: str):
    """Scrape for a comic matching the given title.

    Args:
        title (str): The title of the comic.

    Returns:
        tuple[ComicInfo, str]: A tuple containing the comic info and the cover URL.
    """
