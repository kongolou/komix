from importlib.metadata import PackageNotFoundError, version

import pluggy

try:
    __version__ = version("komix")
except PackageNotFoundError:
    __version__ = "0.1.0"

hookimpl = pluggy.HookimplMarker("komix")
