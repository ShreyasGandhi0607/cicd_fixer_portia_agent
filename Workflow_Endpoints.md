# CI/CD Fixer Agent - Workflow Endpoints

This document lists only the **necessary API endpoints** required to implement the workflow shown in the diagram.

**Base URL:** `https://cicd-fixer-portia-agent.onrender.com/api/v1/`

---

## 1. Get Failures for a Repository

**Endpoint:**  
`GET /failures/repository/{owner}/{repo}?days=30`

**Description:**  
Fetch failed workflow runs for the given repository in the last `N` days (default = 30).

**Response Example:**
```json
[
  {
    "failure_id": 123,
    "repo": "vscode",
    "owner": "microsoft",
    "status": "failed",
    "timestamp": "2025-08-23T12:00:00Z"
  }
]
```

---

## 2. Trigger Portia Analysis

**Endpoint:**  
`POST /portia/analyze`

**Description:**  
Start analysis of a failed workflow run.

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

---

## 3. Check Analysis Status

**Endpoint:**  
`GET /portia/plans/{plan_run_id}/status`

**Description:**  
Poll this endpoint until the analysis is complete.

**Response Example:**
```json
{
  "status": "in_progress"
}
```
or
```json
{
  "status": "completed"
}
```

---

## 4. Fetch Clarifications

**Endpoint:**  
`GET /portia/plans/{plan_run_id}/clarifications`

**Description:**  
Retrieve clarification questions if any. The frontend should display them and allow the user to answer.

**Response Example:**
```json
[
  {
    "clarification_id": "c1",
    "question": "Did you recently update dependencies?"
  }
]
```

---

## 5. Get Fix Suggestions

**Endpoint:**  
`GET /fixes/?owner={owner}&repo={repo}`

**Description:**  
List fixes generated for the repository after analysis.

**Response Example:**
```json
[
  {
    "fix_id": "f123",
    "suggested_fix": "Add null check before accessing property",
    "confidence": 0.85,
    "description": "Fixes TypeError in React component"
  }
]
```

---

## 6. Approve a Fix

**Endpoint:**  
`POST /portia/fixes/{fix_id}/approve`

**Description:**  
Approve a fix, which will trigger a Pull Request.

**Request Example:**
```json
{
  "action": "approve",
  "comment": "Looks good, proceed"
}
```

**Response Example:**
```json
{
  "pr_url": "https://github.com/microsoft/vscode/pull/12345",
  "status": "created"
}
```

---

# ✅ Usage Notes
- Always send requests with `Content-Type: application/json`
- Poll `/portia/plans/{plan_run_id}/status` until `"completed"`
- Show clarifications to the user before proceeding to fixes
- After approval, display `pr_url` to the user
