# Docker Commands for CI/CD Fixer Agent

## 🚀 Quick Start

```bash
# Start everything with one command
./docker-start.sh

# Or manually
docker-compose up --build -d
```

## 📋 Common Commands

### Start Services
```bash
# Build and start in background
docker-compose up --build -d

# Start without rebuilding
docker-compose up -d

# Start with logs visible
docker-compose up --build
```

### Stop Services
```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# Stop and remove containers + images
docker-compose down --rmi all
```

### View Logs
```bash
# View all service logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f redis
```

### Service Management
```bash
# Check service status
docker-compose ps

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart app

# Scale services
docker-compose up -d --scale app=2
```

### Database Operations
```bash
# Access database shell
docker-compose exec db psql -U postgres -d cicd_fixer_db

# Run database backup
docker-compose exec db pg_dump -U postgres cicd_fixer_db > backup.sql

# Check database health
docker-compose exec db pg_isready -U postgres -d cicd_fixer_db
```

### Application Operations
```bash
# Check application health
curl http://localhost:8000/health

# Test Portia integration
curl http://localhost:8000/api/v1/portia/test

# View available tools
curl http://localhost:8000/api/v1/portia/tools
```

## 🔧 Troubleshooting

### Rebuild Everything
```bash
# Remove all containers, images, and volumes
docker-compose down -v --rmi all

# Rebuild from scratch
docker-compose up --build -d
```

### Check Resource Usage
```bash
# View container resource usage
docker stats

# View disk usage
docker system df
```

### Clean Up
```bash
# Remove unused containers, networks, images
docker system prune

# Remove everything unused
docker system prune -a --volumes
```

## 📊 Health Checks

The services include health checks:

- **App**: HTTP health check at `/health`
- **Database**: PostgreSQL connection check
- **Redis**: Redis ping check

## 🌐 Ports

- **App**: 8000 (FastAPI)
- **Database**: 5432 (PostgreSQL)
- **Redis**: 6379 (Redis)

## 📁 Volumes

- **Database**: `postgres_data` (persistent)
- **Logs**: `./logs` (mounted from host)
- **Models**: `./models` (mounted from host)
- **Scripts**: `./scripts` (mounted from host)

## 🚨 Emergency Commands

```bash
# Force stop everything
docker-compose kill

# Remove everything and start fresh
docker-compose down -v --rmi all && docker-compose up --build -d
```
