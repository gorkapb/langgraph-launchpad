import uvicorn

from .api.builder import create_app
from .config.settings import get_settings


def main() -> None:
    """Main entry point for CLI usage."""
    settings = get_settings()
    
    uvicorn.run(
        "langgraph_launchpad.main:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # We handle logging ourselves
    )


if __name__ == "__main__":
    main()