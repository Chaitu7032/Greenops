from typing import Any, Dict, List, Optional
import httpx
import structlog
from app.core.config import settings
from app.services.scorecard_service import SCORECARD_MARKER

logger = structlog.get_logger()


class GitHubService:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GreenOps-FinOps-Bot/1.0",
        }
        if self.token and not self.token.startswith("ghp_dummy"):
            self.headers["Authorization"] = f"Bearer {self.token}"

    def get_pr_files(self, owner: str, repo: str, pull_number: int) -> List[Dict[str, Any]]:
        """Fetch files modified in PR from GitHub REST API."""
        if not self.token or self.token.startswith("ghp_dummy"):
            logger.info("Using mock PR diff files for development", owner=owner, repo=repo, pr=pull_number)
            return [
                {"filename": "app/services/core_service.py", "additions": 45, "deletions": 12, "status": "modified"},
                {"filename": "tests/unit/test_core.py", "additions": 30, "deletions": 5, "status": "modified"},
                {"filename": "README.md", "additions": 4, "deletions": 1, "status": "modified"},
            ]

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, headers=self.headers)
                if res.status_code == 200:
                    return res.json()
                logger.error("GitHub API error fetching files", status=res.status_code, body=res.text)
                return []
        except Exception as e:
            logger.error("Exception fetching GitHub PR files", error=str(e))
            return []

    def post_or_update_pr_comment(self, owner: str, repo: str, pull_number: int, markdown_body: str) -> bool:
        """Find existing GreenOps scorecard comment and update it, or post a new comment."""
        if not self.token or self.token.startswith("ghp_dummy"):
            logger.info("Mocking GitHub PR comment post/update", owner=owner, repo=repo, pr=pull_number)
            return True

        comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_number}/comments"
        try:
            with httpx.Client(timeout=10.0) as client:
                # 1. Look for existing comment with scorecard marker
                res = client.get(comments_url, headers=self.headers)
                if res.status_code == 200:
                    existing_comments = res.json()
                    for comment in existing_comments:
                        if SCORECARD_MARKER in comment.get("body", ""):
                            # Update existing comment
                            comment_id = comment["id"]
                            update_url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}"
                            patch_res = client.patch(update_url, headers=self.headers, json={"body": markdown_body})
                            logger.info("Updated existing PR comment", comment_id=comment_id, status=patch_res.status_code)
                            return patch_res.status_code == 200

                # 2. Otherwise create new comment
                post_res = client.post(comments_url, headers=self.headers, json={"body": markdown_body})
                logger.info("Posted new PR scorecard comment", status=post_res.status_code)
                return post_res.status_code in (200, 201)
        except Exception as e:
            logger.error("Error posting GitHub PR comment", error=str(e))
            return False

    def dispatch_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: str,
        ref: str = "main",
        inputs: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Trigger workflow_dispatch event in GitHub Actions."""
        if not self.token or self.token.startswith("ghp_dummy"):
            logger.info("Mocking GitHub workflow dispatch", owner=owner, repo=repo, workflow=workflow_id, ref=ref)
            return True

        url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
        payload = {"ref": ref, "inputs": inputs or {}}
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, headers=self.headers, json=payload)
                logger.info("Dispatched GitHub Actions workflow", status=res.status_code, workflow=workflow_id)
                return res.status_code == 204
        except Exception as e:
            logger.error("Exception dispatching GitHub workflow", error=str(e))
            return False


github_service = GitHubService()
