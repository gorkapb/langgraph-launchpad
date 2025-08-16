#!/bin/bash
set -e

echo "🚀 Setting up LangGraph Launchpad..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it from https://docs.astral.sh/uv/"
    exit 1
fi

echo "📦 Installing dependencies..."
uv sync

echo "📋 Copying environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
else
    echo "⚠️  .env file already exists, skipping..."
fi

echo "🗄️  Setting up database..."
mkdir -p data

# Ask user for database preference
read -p "🔍 Which database would you like to use? (sqlite/postgresql) [sqlite]: " db_choice
db_choice=${db_choice:-sqlite}

if [ "$db_choice" = "postgresql" ]; then
    echo "🐘 Starting PostgreSQL with Docker..."
    docker-compose up -d postgres
    
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 10
    
    # Update .env file
    sed -i.bak 's/DATABASE_TYPE=sqlite/DATABASE_TYPE=postgresql/' .env
    sed -i.bak 's|DATABASE_URL=sqlite:///./threads.db|DATABASE_URL=postgresql://langgraph:password@localhost:5432/langgraph_db|' .env
    
    echo "✅ PostgreSQL setup complete!"
else
    echo "📁 Using SQLite database"
fi

echo "🧪 Running basic tests..."
uv run python -c "
import sys
sys.path.append('src')
from langgraph_launchpad.config.settings import get_settings
settings = get_settings()
print(f'✅ Configuration loaded successfully')
print(f'📊 Database type: {settings.database_type}')
print(f'🌐 API will run on: {settings.host}:{settings.port}')
"

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Add your OpenAI API key (optional)"
echo "3. Run 'make run' or 'uv run python -m langgraph_launchpad.main'"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "For development:"
echo "- Run 'make dev' to install development dependencies"
echo "- Run 'make test' to run tests"
echo "- Run 'make format' to format code"