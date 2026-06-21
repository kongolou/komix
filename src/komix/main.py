import typer

from . import __version__

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
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    from .routes import STATIC_DIR, router

    web_app = FastAPI(title="KoMiX")
    web_app.include_router(router)
    web_app.mount(
        "/static", StaticFiles(directory=STATIC_DIR, html=True), name="static"
    )
    typer.secho(f"Serving KoMiX at http://{host}:{port}", fg=typer.colors.GREEN)
    uvicorn.run(web_app, host=host, port=port)


if __name__ == "__main__":
    app()
