#!/bin/bash

# Docker Startup Script for CI/CD Fixer Agent
# This script starts the application using Docker commands

set -e

echo "🚀 Starting CI/CD Fixer Agent with Docker"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Please run this script from the cicd_fixer_agent directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Please copy .env.example to .env and configure your environment variables"
    echo "   Required variables:"
    echo "     - GITHUB_TOKEN"
    echo "     - GOOGLE_API_KEY"
    echo "     - GITHUB_WEBHOOK_SECRET"
    echo "     - SECRET_KEY"
    echo "     - DATABASE_URL (optional - will use Docker default)"
    echo ""
    echo "   Optional variables:"
    echo "     - PORTIA_API_KEY"
    echo "     - PORTIA_ENVIRONMENT"
    echo ""
    
    read -p "Do you want to continue without .env file? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Please configure .env file first."
        exit 1
    fi
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down --remove-orphans

# Build and start the services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Check database health
echo "🗄️  Checking database health..."
if docker-compose exec -T db pg_isready -U postgres -d cicd_fixer_db > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "⚠️  Database health check failed, but continuing..."
fi

# Check app health
echo "🌐 Checking application health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy"
else
    echo "⏳ Application is starting up, waiting a bit more..."
    sleep 20
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Application is now healthy"
    else
        echo "❌ Application health check failed"
        echo "   Check logs with: docker-compose logs app"
        exit 1
    fi
fi

echo ""
echo "🎉 CI/CD Fixer Agent is now running!"
echo "====================================="
echo ""
echo "🌐 Application URLs:"
echo "   Main API: http://localhost:8000"
echo "   Documentation: http://localhost:8000/docs"
echo "   Health Check: http://localhost:8000/health"
echo "   Portia Test: http://localhost:8000/api/v1/portia/test"
echo "   Portia Tools: http://localhost:8000/api/v1/portia/tools"
echo ""
echo "🗄️  Database:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: cicd_fixer_db"
echo "   Username: postgres"
echo "   Password: password"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart"
echo "   Rebuild: docker-compose up --build -d"
echo ""
echo "Press Ctrl+C to stop the services"
echo ""

# Keep the script running and show logs
docker-compose logs -f
