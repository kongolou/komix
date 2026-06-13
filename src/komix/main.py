import typer
import uvicorn
from fastapi import FastAPI

from . import __version__
from .routes import router

app = typer.Typer()


@app.command()
def version():
    """
    Print the version of KoMiX.
    """
    typer.secho(f"KoMiX version {__version__}", fg=typer.colors.GREEN)


@app.command()
def serve(host: str = "127.0.0.1", port: int = 7788):
    """
    Serve the KoMiX web UI on the given host and port.
    """
    webapp = FastAPI(title="KoMiX")
    webapp.include_router(router)
    typer.secho(f"Serving KoMiX at http://{host}:{port}", fg=typer.colors.GREEN)
    uvicorn.run(webapp, host=host, port=port)


if __name__ == "__main__":
    app()
