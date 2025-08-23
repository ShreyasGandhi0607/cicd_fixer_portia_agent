# CI/CD Fixer Agent

An AI-powered CI/CD failure analysis and fix generation system that automatically analyzes GitHub Actions workflow failures and provides intelligent fix suggestions using machine learning and AI.

## 🚀 Features

- **Portia AI Framework**: Built on Portia's structured AI agent framework for intelligent CI/CD analysis
- **AI-Powered Analysis**: Uses Google Gemini AI to analyze CI/CD failure logs
- **Machine Learning**: ML-based success prediction for fix suggestions
- **Pattern Recognition**: Identifies common failure patterns across repositories
- **Intelligent Fix Generation**: Generates context-aware fix suggestions using Portia's plan execution
- **GitHub Integration**: Webhook-based automatic failure detection
- **Analytics Dashboard**: Comprehensive failure pattern analysis
- **Multi-Language Support**: Works with JavaScript, Python, Java, C#, and more
- **RESTful API**: Clean, documented API for integration
- **Portia Tools**: 8 specialized tools for CI/CD operations including error classification, fix generation, and GitHub integration

## 🏗️ Architecture

The project follows a clean, modular architecture:

```
cicd_fixer_agent/
├── src/cicd_fixer/           # Main application code
│   ├── api/                  # API layer (FastAPI routes)
│   ├── core/                 # Core configuration and utilities
│   ├── database/             # Database models and repositories
│   ├── services/             # External service integrations
│   ├── analytics/            # ML and pattern analysis
│   ├── models/               # Pydantic data models
│   └── tools/                # Portia AI framework tools
├── tests/                    # Comprehensive test suite
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
└── deployment/               # Docker and Kubernetes configs
```

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: **Google Gemini 2.5 Flash** (fast, cost-effective), scikit-learn
- **AI Framework**: **Portia AI Framework** - Core AI agent orchestration
- **Containerization**: Docker & Docker Compose with health checks
- **API Documentation**: OpenAPI/Swagger
- **Testing**: pytest with async support
- **Code Quality**: Black, flake8, mypy

## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+
- Docker and Docker Compose
- GitHub Personal Access Token
- Google AI API Key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd cicd_fixer_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
DATABASE_URL=postgresql://username:password@localhost:5432/cicd_fixer_db
GITHUB_TOKEN=your_github_personal_access_token
GOOGLE_API_KEY=your_google_ai_api_key
GITHUB_WEBHOOK_SECRET=your_webhook_secret
SECRET_KEY=your_secret_key_here
```

### 3. Database Setup

```bash
# Run database setup script
python scripts/setup_db.py
```

### 4. Start the Application

```bash
# Using Docker (recommended)
./docker-start.sh

# Or manually with Docker Compose
docker-compose up --build -d

# Or manually without Docker
./start.sh

# Or manually with uvicorn
uvicorn cicd_fixer.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Application

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Portia Test**: http://localhost:8000/api/v1/portia/test
- **Portia Tools**: http://localhost:8000/api/v1/portia/tools

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `GITHUB_TOKEN` | GitHub Personal Access Token | - |
| `GOOGLE_API_KEY` | Google AI API Key | - |
| `GITHUB_WEBHOOK_SECRET` | GitHub webhook secret | - |
| `SECRET_KEY` | Application secret key | - |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### GitHub Webhook Setup

1. Go to your GitHub repository
2. Navigate to Settings → Webhooks
3. Add webhook with URL: `https://your-domain.com/api/v1/webhook/github`
4. Set content type to `application/json`
5. Select events: `Workflow runs`
6. Set webhook secret (same as `GITHUB_WEBHOOK_SECRET`)

## 📚 API Endpoints

### Core Endpoints

- `GET /` - Application information
- `GET /health` - Health check
- `GET /docs` - API documentation

### Analysis Endpoints

- `POST /api/v1/analysis/workflow` - Analyze workflow failure
- `POST /api/v1/analysis/ml-prediction` - ML-based success prediction
- `POST /api/v1/analysis/generate-fix` - Generate intelligent fix

### Webhook Endpoints

- `POST /api/v1/webhook/github` - GitHub webhook handler

### Health Endpoints

- `GET /api/v1/health/` - Comprehensive health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

## 🧪 Testing

```bash
# Test Portia integration
python scripts/test_portia.py

# Run demo
python scripts/demo.py

# Run all tests
pytest

# Run with coverage
pytest --cov=cicd_fixer

# Run specific test category
pytest tests/test_api/
pytest tests/test_services/
pytest tests/test_analytics/
```

## 🐳 Docker Deployment

### Development

```bash
docker-compose up --build
```

### Production

```bash
# Build production image
docker build -t cicd-fixer-agent:latest .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e GITHUB_TOKEN=your_token \
  -e GOOGLE_API_KEY=your_key \
  cicd-fixer-agent:latest
```

## 📊 Monitoring and Analytics

The system provides comprehensive analytics:

- **Failure Pattern Analysis**: Identifies common failure types
- **Success Rate Tracking**: Monitors fix effectiveness
- **ML Model Performance**: Tracks prediction accuracy
- **Repository Learning**: Builds knowledge base per repository
- **Performance Metrics**: Response times and throughput

## 🔒 Security Features

- GitHub webhook signature verification
- Environment-based configuration
- Secure database connections
- Input validation and sanitization
- Rate limiting (configurable)
- CORS protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints throughout
- Write comprehensive docstrings
- Maintain test coverage above 80%
- Use conventional commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Wiki**: Additional documentation and examples

## 🔮 Roadmap

- [ ] Real-time failure notifications
- [ ] Advanced ML model training pipeline
- [ ] Integration with more CI/CD platforms
- [ ] Mobile application
- [ ] Advanced analytics dashboard
- [ ] Multi-tenant support
- [ ] API rate limiting and quotas

## 🙏 Acknowledgments

- Google Gemini AI for intelligent analysis
- Portia AI framework for ML capabilities
- FastAPI for the excellent web framework
- PostgreSQL for reliable data storage
- The open-source community for inspiration

---

**Built with ❤️ for the DevOps community**
