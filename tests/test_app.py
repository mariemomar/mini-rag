
from fastapi import FastAPI

from src.main import app


def test_app_is_fastapi_application():
    """The application should load as a FastAPI instance."""
    assert isinstance(app, FastAPI)


def test_app_has_registered_routes():
    """The app should register routes beyond FastAPI's built-in docs."""
    paths = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    built_in_paths = {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}

    assert paths - built_in_paths, "No application routes were registered"
