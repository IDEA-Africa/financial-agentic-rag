#!/bin/bash

# Build script for Agentic RAG application
set -e

echo "🐋 Building Agentic RAG Docker Images"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your Azure configuration before running."
    exit 1
fi

# Build backend
echo "🏗️  Building backend image..."
docker build -t fintech-agentic-backend:latest ./backend

# Build frontend
echo "🏗️  Building frontend image..."
docker build -t fintech-agentic-frontend:latest ./frontend

echo "✅ Build completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   docker-compose up -d"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
