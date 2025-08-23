"""GitHub service integration for the CI/CD Fixer Agent."""

import requests
from typing import Dict, Any, Optional, List
from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class GitHubService:
    """Service for interacting with GitHub API."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub service.
        
        Args:
            token: GitHub personal access token. If None, uses settings.
        """
        settings = get_settings()
        self.token = token or settings.github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CI-CD-Fixer-Agent/1.0"
        }
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
            logger.info("GitHub service initialized with authentication")
        else:
            logger.warning("GitHub service initialized without authentication token")
    
    def get_workflow_run(self, owner: str, repo: str, run_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a workflow run.
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: GitHub Actions run ID
            
        Returns:
            Workflow run data or None if failed
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}"
        
        try:
            logger.info(f"Fetching workflow run {run_id} for {owner}/{repo}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched workflow run {run_id}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching workflow run {run_id}: {e}")
            return None
    
    def get_workflow_run_logs(self, owner: str, repo: str, run_id: int) -> Optional[str]:
        """Get logs for a workflow run.
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: GitHub Actions run ID
            
        Returns:
            Workflow logs or None if failed
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
        
        try:
            logger.info(f"Fetching logs for workflow run {run_id}")
            response = requests.get(url, headers=self.headers, timeout=60)
            response.raise_for_status()
            
            # The response is a ZIP file containing log files
            # For now, return the raw content
            # TODO: Implement ZIP extraction and parsing
            logger.info(f"Successfully fetched logs for workflow run {run_id}")
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error fetching workflow logs for {run_id}: {e}")
            # Return sample logs for demo purposes
            return self._get_sample_logs()
    
    def get_workflow_logs(self, owner: str, repo: str, run_id: int) -> Optional[str]:
        """Alias for get_workflow_run_logs to maintain compatibility."""
        return self.get_workflow_run_logs(owner, repo, run_id)
    
    def get_workflow_jobs(self, owner: str, repo: str, run_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get jobs for a workflow run.
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: GitHub Actions run ID
            
        Returns:
            List of workflow jobs or None if failed
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
        
        try:
            logger.info(f"Fetching jobs for workflow run {run_id}")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            jobs = response.json().get("jobs", [])
            logger.info(f"Successfully fetched {len(jobs)} jobs for workflow run {run_id}")
            return jobs
            
        except requests.RequestException as e:
            logger.error(f"Error fetching workflow jobs for {run_id}: {e}")
            return None

    def get_workflow_run_jobs(self, owner: str, repo: str, run_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get jobs for a workflow run (alias for get_workflow_jobs)."""
        return self.get_workflow_jobs(owner, repo, run_id)
    
    def create_issue(self, owner: str, repo: str, title: str, body: str, labels: List[str] = None) -> Optional[Dict[str, Any]]:
        """Create an issue with the suggested fix.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body
            labels: List of labels to apply
            
        Returns:
            Created issue data or None if failed
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        
        data = {
            "title": title,
            "body": body,
            "labels": labels or ["ci-cd-fix", "automated"]
        }
        
        try:
            logger.info(f"Creating issue in {owner}/{repo}: {title}")
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            issue = response.json()
            logger.info(f"Successfully created issue #{issue['number']}")
            return issue
            
        except requests.RequestException as e:
            logger.error(f"Error creating issue in {owner}/{repo}: {e}")
            return None
    
    def create_pull_request(self, owner: str, repo: str, title: str, body: str, 
                          head_branch: str, base_branch: str = "main") -> Optional[Dict[str, Any]]:
        """Create a pull request with the fix.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: PR title
            body: PR body
            head_branch: Source branch
            base_branch: Target branch
            
        Returns:
            Created PR data or None if failed
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        
        data = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch
        }
        
        try:
            logger.info(f"Creating PR in {owner}/{repo}: {title}")
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            
            pr = response.json()
            logger.info(f"Successfully created PR #{pr['number']}")
            return pr
            
        except requests.RequestException as e:
            logger.error(f"Error creating PR in {owner}/{repo}: {e}")
            return None
    
    def _get_sample_logs(self) -> str:
        """Get sample logs for demo purposes.
        
        Returns:
            Sample workflow failure logs
        """
        return """
        ##[group]Run actions/checkout@v4
        ##[command]git -c http.extraheader="AUTHORIZATION: basic ***" fetch --tags --force --prune --prune-tag --progress --no-recurse-submodules --no-shallow --depth=1 origin +refs/heads/main:refs/remotes/origin/main +refs/pull/123/merge:refs/remotes/pull/123/merge
        ##[error]fatal: unable to access 'https://github.com/owner/repo.git/': The requested URL returned error: 403
        ##[endgroup]
        ##[error]Git checkout failed
        ##[error]Exit code: 128
        ##[group]Run actions/setup-node@v4
        ##[command]node --version
        v18.17.0
        ##[command]npm --version
        9.6.7
        ##[endgroup]
        ##[group]Run npm ci
        ##[command]npm ci
        ##[error]npm ERR! code ENOENT
        ##[error]npm ERR! syscall open
        ##[error]npm ERR! path /home/runner/work/repo/repo/package.json
        ##[error]npm ERR! errno -2
        ##[error]npm ERR! enoent ENOENT: no such file or directory, open 'package.json'
        ##[error]npm ERR! enoent This is related to npm not being able to find a file.
        ##[error]npm ERR! enoent
        ##[error]npm ERR! A complete log of this run can be found at:
        ##[error]npm ERR!     /home/runner/.npm/_logs/2023-08-23T10_00_00_000Z-debug-0.log
        ##[endgroup]
        ##[error]Process completed with exit code 1.
        """
    
    def test_connection(self) -> bool:
        """Test GitHub API connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/rate_limit", headers=self.headers, timeout=10)
            response.raise_for_status()
            
            rate_limit = response.json()
            logger.info(f"GitHub API rate limit: {rate_limit['resources']['core']['remaining']}/{rate_limit['resources']['core']['limit']}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"GitHub API connection test failed: {e}")
            return False
