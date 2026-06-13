import pluggy

hookspec = pluggy.HookspecMarker("komix")


@hookspec
def search(query: str):
    """Search for comics matching the given query.

    Args:
        query (str): The search query.

    Returns:
        list[ComicInfo]: A list of comics matching the query.
    """


@hookspec
def fetch_comicinfo(comic_id: str):
    """Get the comic info for the given comic ID.

    Args:
        comic_id (str): The comic ID.

    Returns:
        ComicInfo: The comic info.
    """


@hookspec
def fetch_cover_url(comic_id: str):
    """Get the cover URL for the given comic ID.

    Args:
        comic_id (str): The comic ID.

    Returns:
        str: The cover URL.
    """
