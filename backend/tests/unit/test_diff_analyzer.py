from app.services.diff_analyzer import classify_file, analyze_pr_diff


def test_classify_file_types():
    assert classify_file("backend/app/main.py") == "source"
    assert classify_file("frontend/src/App.tsx") == "source"
    assert classify_file("backend/tests/unit/test_core.py") == "test"
    assert classify_file("tests/e2e/test_checkout.spec.ts") == "integration"
    assert classify_file("README.md") == "doc"
    assert classify_file("docs/api.md") == "doc"
    assert classify_file(".github/workflows/ci.yml") == "ci"
    assert classify_file("Dockerfile") == "infra_config"
    assert classify_file("package.json") == "infra_config"


def test_analyze_pr_diff():
    mock_files = [
        {"filename": "app/models/user.py", "additions": 50, "deletions": 10},
        {"filename": "tests/unit/test_user.py", "additions": 40, "deletions": 5},
        {"filename": "tests/e2e/test_flow.spec.ts", "additions": 80, "deletions": 20},
        {"filename": "README.md", "additions": 5, "deletions": 0},
        {"filename": ".github/workflows/deploy.yml", "additions": 15, "deletions": 2},
    ]

    res = analyze_pr_diff(mock_files)
    assert res.changed_files_count == 5
    assert res.lines_added == 190
    assert res.lines_deleted == 37
    assert res.source_files_count == 1
    assert res.test_files_count == 1
    assert res.integration_files_count == 1
    assert res.documentation_files_count == 1
    assert res.configuration_files_count == 1
