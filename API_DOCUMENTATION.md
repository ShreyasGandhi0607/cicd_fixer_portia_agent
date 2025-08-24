# CI/CD Fixer Agent API Documentation

**Base URL:** `https://cicd-fixer-portia-agent.onrender.com/api/v1/`

---

## 📌 Health Endpoints

### `GET /health/`
**Description:** Basic health check.  
**Response Example:**
```json
"string"
````

### `GET /api/v1/health/`

**Description:** Check overall health of the application and its services.
**Response Example:**

```json
{
  "status": "healthy",
  "timestamp": "2025-08-23T10:00:00.000Z",
  "services": {
    "db": "ok",
    "cache": "ok"
  }
}
```

### `GET /api/v1/health/ready`

**Description:** Check if the application is ready to serve requests.
**Response Example:** `"ready"`

### `GET /api/v1/health/live`

**Description:** Check if the application is alive and responding.
**Response Example:** `"alive"`

---

## 📌 Analysis Endpoints

### `POST /api/v1/analysis/workflow`

**Description:** Analyze a GitHub Actions workflow failure and suggest fixes.
**Request Example:**

```json
{
  "owner": "microsoft",
  "repo": "vscode",
  "run_id": 17152193292
}
```

**Response Example:**

```json
{
  "message": "Analysis triggered successfully",
  "failure_id": "7",
  "owner": "microsoft",
  "repo": "vscode",
  "run_id": 17152193292
}
```

### `POST /api/v1/analysis/ml-prediction`

**Description:** Predict the success likelihood of a suggested fix using ML.
**Request Example:**

```json
{
  "error_log": "npm install failed with ENOENT error",
  "suggested_fix": "Run npm install --legacy-peer-deps",
  "repo_context": "Node.js application with package.json",
  "error_type": "dependency_error",
  "language": "javascript"
}
```

**Response Example:**

```json
{
  "prediction": "likely_success",
  "confidence": 0.92,
  "factors": ["dependency issue"],
  "recommendation": "Proceed with fix"
}
```

### `POST /api/v1/analysis/generate-fix`

**Description:** Generate an intelligent fix using ML and AI analysis.
**Request Example:**

```json
{
  "error_log": "TypeError: Cannot read property of undefined",
  "repo_context": "React TypeScript application",
  "error_type": "test_failure",
  "language": "typescript"
}
```

**Response Example:**

```json
{
  "fix_id": "12345",
  "suggested_fix": "Add null check before property access",
  "confidence": 0.85,
  "reasoning": "Common fix for undefined property access",
  "created_at": "2025-08-24T12:59:12.588Z"
}
```

---

## 📌 Webhook

### `POST /api/v1/webhook/github`

**Description:** Handle GitHub webhook events.
**Headers:**

* `x-hub-signature-256`: optional
* `x-hub-signature`: optional

**Request Example:**

```json
{
  "action": "completed",
  "workflow_run": { "id": 123 },
  "repository": { "full_name": "microsoft/vscode" },
  "sender": "octocat"
}
```

**Response Example:**

```json
{
  "processed": true,
  "message": "Webhook processed",
  "workflow_run_id": 123,
  "timestamp": "2025-08-24T12:59:12.590Z"
}
```

---

## 📌 Fixes

### `GET /api/v1/fixes/`

**Description:** Get all pending fixes.

### `GET /api/v1/fixes/{fix_id}`

**Description:** Get detailed information about a specific fix.

### `POST /api/v1/fixes/{fix_id}/approve`

**Description:** Approve a suggested fix.
**Request Example:**

```json
{
  "action": "approve",
  "comment": "Looks good"
}
```

### `POST /api/v1/fixes/{fix_id}/reject`

**Description:** Reject a suggested fix.
**Request Example:**

```json
{
  "action": "reject",
  "comment": "Not applicable"
}
```

### `GET /api/v1/fixes/history/{owner}/{repo}`

**Description:** Get fix history for a repository.
**Params:** `limit=50` (default)

---

## 📌 Failures

### `GET /api/v1/failures/`

**Description:** Get all workflow failures. Supports filters `limit` and `status`.

### `GET /api/v1/failures/{failure_id}`

**Description:** Get detailed failure info.

### `GET /api/v1/failures/repository/{owner}/{repo}?days=30`

**Description:** Get failures for a specific repository in the last N days.

### `GET /api/v1/failures/statistics/summary`

**Description:** Get summary statistics of failures.

---

## 📌 Analytics

* `GET /api/v1/analytics/patterns` → Failure patterns
* `GET /api/v1/analytics/effectiveness` → Fix effectiveness stats
* `GET /api/v1/analytics/repository/{owner}/{repo}` → Repo profile
* `GET /api/v1/analytics/dashboard` → Analytics dashboard
* `POST /api/v1/analytics/ml/similar-fixes` → Find similar fixes
* `POST /api/v1/analytics/ml/predict-success` → Predict fix success
* `POST /api/v1/analytics/ml/generate-enhanced-fix` → Generate enhanced fix
* `POST /api/v1/analytics/ml/learn-from-feedback` → Improve model with feedback
* `GET /api/v1/analytics/ml/pattern-insights` → Get ML insights
* `GET /api/v1/analytics/ml/model-performance` → Get ML performance metrics
* `POST /api/v1/analytics/ml/fix-suggestions` → Generate fix suggestions

---

## 📌 Portia (Plan-based Analysis)

* `POST /api/v1/portia/analyze` → Trigger Portia analysis
* `GET /api/v1/portia/plans/{plan_run_id}/status` → Check analysis status
* `GET /api/v1/portia/plans/{plan_run_id}/clarifications` → List clarifications
* `POST /api/v1/portia/clarifications/{plan_run_id}/{clarification_id}` → Respond to clarification
* `POST /api/v1/portia/fixes/{fix_id}/approve` → Approve fix and create PR
* `POST /api/v1/portia/fixes/{fix_id}/reject` → Reject fix
* `GET /api/v1/portia/tools` → List available Portia tools
* `GET /api/v1/portia/health` → Portia health check

---

## ✅ Notes

* All endpoints return JSON.
* Use `Content-Type: application/json`.
* Errors follow FastAPI validation schema:

```json
{
  "detail": [
    {
      "loc": ["field"],
      "msg": "error message",
      "type": "validation_error"
    }
  ]
}
```

---