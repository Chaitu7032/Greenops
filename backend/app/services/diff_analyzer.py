from typing import Any, Dict, List
import re

# File classification patterns
SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".c", ".cpp",
    ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".scala"
}

TEST_PATTERNS = [
    r"(^|/)(test_|tests/|__tests__/|spec/|specs/|it/)",
    r"(_test|\.test|\.spec)\.(py|js|jsx|ts|tsx|go|rs|java|rb|php)$"
]

INTEGRATION_PATTERNS = [
    r"(^|/)(integration|e2e|smoke|benchmark|load)/",
    r"(_integration_test|\.e2e_test|\.e2e\.spec)\."
]

DOC_PATTERNS = [
    r"\.(md|rst|txt|adoc|pdf)$",
    r"(^|/)(docs|documentation|doc)/",
    r"^LICENSE",
    r"^CHANGELOG"
]

CI_CONFIG_PATTERNS = [
    r"^\.github/(workflows|actions)/",
    r"^\.gitlab-ci\.yml",
    r"^\.circleci/",
    r"^Jenkinsfile",
    r"^\.travis\.yml",
    r"^azure-pipelines\.yml"
]

CONFIG_INFRA_PATTERNS = [
    r"(Dockerfile|docker-compose|compose\.yml|compose\.yaml)",
    r"\.(ya?ml|json|toml|ini|env\.example|tf|hcl)$",
    r"(^|/)(terraform|k8s|helm|deploy|scripts)/",
    r"(package\.json|pyproject\.toml|requirements\.txt|Cargo\.toml|go\.mod|pom\.xml|build\.gradle)"
]


class DiffAnalysisResult:
    def __init__(
        self,
        changed_files_count: int,
        lines_added: int,
        lines_deleted: int,
        source_files_count: int,
        test_files_count: int,
        documentation_files_count: int,
        configuration_files_count: int,
        integration_files_count: int,
        raw_files: List[str]
    ):
        self.changed_files_count = changed_files_count
        self.lines_added = lines_added
        self.lines_deleted = lines_deleted
        self.source_files_count = source_files_count
        self.test_files_count = test_files_count
        self.documentation_files_count = documentation_files_count
        self.configuration_files_count = configuration_files_count
        self.integration_files_count = integration_files_count
        self.raw_files = raw_files

    def to_dict(self) -> Dict[str, Any]:
        return {
            "changed_files_count": self.changed_files_count,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
            "source_files_count": self.source_files_count,
            "test_files_count": self.test_files_count,
            "documentation_files_count": self.documentation_files_count,
            "configuration_files_count": self.configuration_files_count,
            "integration_files_count": self.integration_files_count,
        }


def classify_file(filename: str) -> str:
    """
    Deterministically classify a file into:
    integration, test, ci, infra_config, doc, source, other
    """
    fn = filename.strip()

    # 1. Integration tests
    for pattern in INTEGRATION_PATTERNS:
        if re.search(pattern, fn, re.IGNORECASE):
            return "integration"

    # 2. CI/CD files
    for pattern in CI_CONFIG_PATTERNS:
        if re.search(pattern, fn, re.IGNORECASE):
            return "ci"

    # 3. Unit / standard tests
    for pattern in TEST_PATTERNS:
        if re.search(pattern, fn, re.IGNORECASE):
            return "test"

    # 4. Documentation
    for pattern in DOC_PATTERNS:
        if re.search(pattern, fn, re.IGNORECASE):
            return "doc"

    # 5. Infrastructure / Configuration
    for pattern in CONFIG_INFRA_PATTERNS:
        if re.search(pattern, fn, re.IGNORECASE):
            return "infra_config"

    # 6. Source code by extension
    for ext in SOURCE_EXTENSIONS:
        if fn.endswith(ext):
            return "source"

    return "other"


def analyze_pr_diff(files_data: List[Dict[str, Any]]) -> DiffAnalysisResult:
    """
    Analyze files list (e.g. from GitHub API `GET /repos/{owner}/{repo}/pulls/{pull_number}/files`).
    """
    total_files = len(files_data)
    lines_added = sum(f.get("additions", 0) for f in files_data)
    lines_deleted = sum(f.get("deletions", 0) for f in files_data)

    source_cnt = 0
    test_cnt = 0
    doc_cnt = 0
    config_cnt = 0
    integration_cnt = 0
    raw_files = []

    for f in files_data:
        filename = f.get("filename", "")
        raw_files.append(filename)
        cat = classify_file(filename)

        if cat == "source":
            source_cnt += 1
        elif cat == "test":
            test_cnt += 1
        elif cat == "integration":
            integration_cnt += 1
        elif cat in ("ci", "infra_config"):
            config_cnt += 1
        elif cat == "doc":
            doc_cnt += 1

    return DiffAnalysisResult(
        changed_files_count=total_files,
        lines_added=lines_added,
        lines_deleted=lines_deleted,
        source_files_count=source_cnt,
        test_files_count=test_cnt,
        documentation_files_count=doc_cnt,
        configuration_files_count=config_cnt,
        integration_files_count=integration_cnt,
        raw_files=raw_files
    )
