from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.sqlite import SqliteSaver

from langgraph_launchpad.config.settings import get_settings


def create_checkpointer():
    """Create appropriate checkpointer based on database type."""
    settings = get_settings()
    
    if settings.is_postgresql:
        return PostgresSaver.from_conn_string(settings.database_url)
    else:
        # Extract database path from SQLite URL
        db_path = settings.database_url.replace("sqlite:///", "")
        return SqliteSaver.from_conn_string(db_path)


# Create global checkpointer instance
checkpointer = create_checkpointer()