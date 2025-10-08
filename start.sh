#!/bin/bash

# Reservoir GHG Emissions Tool - Startup Script
# For Ubuntu 22.04

set -e

echo "======================================"
echo "Reservoir GHG Emissions Tool"
echo "IPCC Tier 1 Methodology"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   sudo apt update"
    echo "   sudo apt install docker.io docker-compose -y"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first:"
    echo "   sudo apt update"
    echo "   sudo apt install docker-compose -y"
    exit 1
fi

# Create data directory if it doesn't exist
echo "📁 Creating data directory..."
mkdir -p data

# Check if container is already running
if docker ps | grep -q "reservoir-emissions-tool"; then
    echo "⚠️  Container is already running!"
    echo ""
    echo "Choose an action:"
    echo "1) Restart the container"
    echo "2) Stop the container"
    echo "3) View logs"
    echo "4) Exit"
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1)
            echo "🔄 Restarting container..."
            docker-compose restart
            ;;
        2)
            echo "⏹️  Stopping container..."
            docker-compose stop
            exit 0
            ;;
        3)
            echo "📋 Viewing logs (Ctrl+C to exit)..."
            docker-compose logs -f
            exit 0
            ;;
        4)
            exit 0
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
else
    # Build and start the container
    echo "🏗️  Building Docker image..."
    docker-compose build
    
    echo "🚀 Starting container..."
    docker-compose up -d
    
    # Wait for container to be ready
    echo "⏳ Waiting for application to start..."
    sleep 3
    
    # Check if container is running
    if docker ps | grep -q "reservoir-emissions-tool"; then
        echo "✅ Container started successfully!"
    else
        echo "❌ Container failed to start. Checking logs..."
        docker-compose logs
        exit 1
    fi
fi

echo ""
echo "======================================"
echo "✅ Application is running!"
echo "======================================"
echo ""
echo "🌐 Access the application at:"
echo "   http://localhost:8000"
echo ""
echo "📚 API Documentation at:"
echo "   http://localhost:8000/docs"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "⏹️  To stop:"
echo "   docker-compose stop"
echo ""
echo "🗑️  To remove:"
echo "   docker-compose down"
echo ""
echo "======================================"
