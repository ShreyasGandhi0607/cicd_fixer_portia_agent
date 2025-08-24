# CI/CD Fixer Agent

An AI-powered CI/CD failure analysis and fix generation system that automatically analyzes GitHub Actions workflow failures and provides intelligent fix suggestions using machine learning and AI.

**Deployed API:** [https://cicd-fixer-portia-agent.onrender.com](https://cicd-fixer-portia-agent.onrender.com)  
**API Docs:** [https://cicd-fixer-portia-agent.onrender.com/docs](https://cicd-fixer-portia-agent.onrender.com/docs)

---

## 🚀 Features

- **Portia AI Framework**: Structured AI agent framework for CI/CD analysis
- **AI-Powered Analysis**: Uses Gemini AI to analyze CI/CD failure logs
- **Machine Learning**: ML-based success prediction for fix suggestions
- **Pattern Recognition**: Identifies common failure patterns across repositories
- **Intelligent Fix Generation**: Context-aware fixes with confidence scoring
- **GitHub Integration**: Webhook-based automatic failure detection
- **Analytics Dashboard**: Failure statistics & insights
- **Multi-Language Support**: Works with JS, Python, Java, C#, etc.
- **RESTful API**: Well-structured API endpoints
- **Portia Tools**: Specialized tools for CI/CD operations

---

## 🏗️ Architecture

```

cicd\_fixer\_agent/
├── src/cicd\_fixer/           # Main application code
│   ├── api/                  # API layer (FastAPI routes)
│   ├── core/                 # Core configuration and utilities
│   ├── database/             # Database models and repositories
│   ├── services/             # External service integrations
│   ├── analytics/            # ML and pattern analysis
│   ├── models/               # Pydantic data models
│   └── tools/                # Portia AI framework tools
├── tests/                    # Test suite
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
└── deployment/               # Docker & Kubernetes configs

````

---

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL
- **AI/ML**: Google Gemini 2.5 Flash, scikit-learn
- **AI Framework**: Portia AI Framework
- **Containerization**: Docker & Docker Compose
- **API Docs**: OpenAPI/Swagger
- **Testing**: pytest

---

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose
- GitHub Personal Access Token
- Google AI API Key
- Portia API Key

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd cicd_fixer_agent
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
````

### 2. Configure Environment

```bash
cp .env.example .env
```

Update `.env`:

```
GOOGLE_API_KEY= # your_google_ai_api_key
DATABASE_URL=postgres://postgres:postgres@localhost:5432/mydb
GITHUB_TOKEN=  # Your GitHub token for API access
GITHUB_WEBHOOK_SECRET= # Your GitHub webhook secret for secure communication
PORTIA_API_KEY=     # Your Portia API key
```

### 3. Run Application

```bash
# Docker
docker-compose up --build -d

# Or manual
uvicorn cicd_fixer.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access

* **Base API**: [https://cicd-fixer-portia-agent.onrender.com](https://cicd-fixer-portia-agent.onrender.com)
* **Docs**: [https://cicd-fixer-portia-agent.onrender.com/docs](https://cicd-fixer-portia-agent.onrender.com/docs)
* **Health**: [https://cicd-fixer-portia-agent.onrender.com/api/v1/health/](https://cicd-fixer-portia-agent.onrender.com/api/v1/health/)

---

## 📚 Core API Endpoints

### 🔹 Health

* `GET /api/v1/health/` → Health check
* `GET /api/v1/health/ready` → Readiness check
* `GET /api/v1/health/live` → Liveness check

### 🔹 Workflow Analysis

* `POST /api/v1/analysis/workflow` → Analyze a workflow failure
* `POST /api/v1/analysis/ml-prediction` → Predict fix success
* `POST /api/v1/analysis/generate-fix` → Generate fix suggestion

### 🔹 Portia (Plan-based Analysis)

* `POST /api/v1/portia/analyze` → Start analysis
* `GET /api/v1/portia/plans/{plan_run_id}/status` → Poll analysis status
* `GET /api/v1/portia/plans/{plan_run_id}/clarifications` → Get clarifications
* `POST /api/v1/portia/clarifications/{plan_run_id}/{clarification_id}` → Respond to clarification
* `POST /api/v1/portia/fixes/{fix_id}/approve` → Approve fix & create PR
* `POST /api/v1/portia/fixes/{fix_id}/reject` → Reject fix

### 🔹 Fixes

* `GET /api/v1/fixes/?owner={owner}&repo={repo}` → Get fixes for repo
* `GET /api/v1/fixes/{fix_id}` → Fix details
* `POST /api/v1/fixes/{fix_id}/approve` → Approve fix
* `POST /api/v1/fixes/{fix_id}/reject` → Reject fix
* `GET /api/v1/fixes/history/{owner}/{repo}` → Fix history

### 🔹 Failures

* `GET /api/v1/failures/` → All failures
* `GET /api/v1/failures/{failure_id}` → Failure detail
* `GET /api/v1/failures/repository/{owner}/{repo}?days=30` → Failures for repo
* `GET /api/v1/failures/statistics/summary` → Failure stats

### 🔹 Analytics

* `GET /api/v1/analytics/patterns` → Failure patterns
* `GET /api/v1/analytics/effectiveness` → Fix effectiveness
* `GET /api/v1/analytics/repository/{owner}/{repo}` → Repo analytics
* `GET /api/v1/analytics/dashboard` → Dashboard
* `POST /api/v1/analytics/ml/similar-fixes` → Similar fixes
* `POST /api/v1/analytics/ml/predict-success` → Predict fix success
* `POST /api/v1/analytics/ml/generate-enhanced-fix` → Generate enhanced fix
* `POST /api/v1/analytics/ml/learn-from-feedback` → Learn from feedback
* `GET /api/v1/analytics/ml/pattern-insights` → ML insights
* `GET /api/v1/analytics/ml/model-performance` → ML performance
* `POST /api/v1/analytics/ml/fix-suggestions` → Generate fix suggestions

### 🔹 Webhook

* `POST /api/v1/webhook/github` → GitHub webhook

---

## ✅ Workflow Endpoints

1. `GET /api/v1/failures/repository/{owner}/{repo}?days=30`
2. `POST /api/v1/portia/analyze`
3. `GET /api/v1/portia/plans/{plan_run_id}/status`
4. `GET /api/v1/portia/plans/{plan_run_id}/clarifications`
5. `GET /api/v1/fixes/?owner={owner}&repo={repo}`
6. `POST /api/v1/portia/fixes/{fix_id}/approve`

---

## 🧪 Testing

```bash
pytest
pytest --cov=cicd_fixer
```

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

or

```bash
docker run -d -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e GITHUB_TOKEN=your_token \
  -e GOOGLE_API_KEY=your_key \
  cicd-fixer-agent:latest
```

---

## 📊 Monitoring & Analytics

* Failure statistics
* Fix effectiveness
* Model performance

---

## 🔒 Security

* Webhook signature verification
* Input validation
* Secure DB connections

---

## 🆘 Support

* Docs: [API Docs](https://cicd-fixer-portia-agent.onrender.com/docs)
* Issues: GitHub Issues

---

**Built with ❤️ for the DevOps community**
