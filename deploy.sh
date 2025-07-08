#!/bin/bash

# Facebook Event Scraper Deploy Script
# Commits changes to GitHub and rebuilds Docker container

echo "🎵 Deploying Facebook Event Scraper..."

# Change to project directory (update this path for your setup)
PROJECT_DIR=${PROJECT_DIR:-$(pwd)}
cd "$PROJECT_DIR" || { echo "❌ Project folder not found: $PROJECT_DIR"; exit 1; }

echo "📁 Current directory: $(pwd)"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Creating from example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "📋 Please edit .env file with your configuration before running the scraper"
    else
        echo "❌ No .env.example file found. Please create .env manually."
        exit 1
    fi
fi

# Check Git status
echo "📊 Checking Git status..."
git status

# Add all changes (excluding .env files due to .gitignore)
echo "➕ Adding changes to Git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit with timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "💾 Committing changes..."
    git commit -m "Auto commit: Facebook scraper updates - $TIMESTAMP"
    
    # Push to GitHub
    echo "🚀 Pushing to GitHub..."
    git push origin main || git push origin master || { echo "❌ Git push failed"; exit 1; }
    echo "✅ Successfully pushed to GitHub"
fi

# Rebuild and restart Docker container
echo "🐳 Rebuilding Docker container..."
sudo docker-compose down

echo "🔨 Building new image with latest changes..."
sudo docker-compose up -d --build

# Wait a moment for container to start
sleep 3

# Check if container is running
if sudo docker ps | grep -q facebook-scraper; then
    echo "✅ Container is running successfully"
    echo "🧪 Testing scraper (optional)..."
    echo "Run this command to test: sudo docker exec -it facebook-scraper python scraper.py"
else
    echo "❌ Container failed to start"
    echo "Check logs with: sudo docker-compose logs facebook-scraper"
fi

echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "   • Test scraper: sudo docker exec -it facebook-scraper python scraper.py"
echo "   • Check logs: sudo docker-compose logs -f facebook-scraper"
echo "   • Edit config: nano .env"
echo ""
echo "📊 Monitor your events at your N8N webhook endpoint"