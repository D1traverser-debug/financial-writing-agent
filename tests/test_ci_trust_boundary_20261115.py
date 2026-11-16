from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_pull_request_ci_never_receives_repository_secrets_or_tokens():
    workflow = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")

    # This workflow checks out and executes pull-request-head code. It must
    # therefore have no path to any repository secret, even behind an if
    # condition: a PR can change the workflow definition itself.
    assert "secrets." not in workflow
    assert "GITHUB_TOKEN" not in workflow
    assert "FINANCIAL_PROVIDER_ATTESTATION_KEY" not in workflow
    assert "FINANCIAL_TRUSTED_PROVIDER_ID" not in workflow
    assert "FINANCIAL_OWNER_PRINCIPAL" not in workflow
    assert "pull_request:" in workflow
    assert "permissions:\n  contents: read" in workflow


def test_privileged_archive_workflow_is_manual_main_only_and_checks_out_trusted_sha():
    workflow = (WORKFLOWS / "branch_archive_once.yml").read_text(encoding="utf-8")

    assert "on:\n  workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow
    assert "\n  push:" not in workflow
    assert "if: ${{ github.ref == 'refs/heads/main' && inputs.start_archive == true }}" in workflow
    assert workflow.count("ref: ${{ github.sha }}") == 3
    assert workflow.count("persist-credentials: false") == 3
    assert "environment:\n      name: financial-branch-archive" in workflow
    assert "environment:\n      name: financial-branch-prune" in workflow


def test_no_other_workflow_may_reference_custom_provider_or_archive_secrets():
    for path in WORKFLOWS.glob("*.yml"):
        if path.name == "branch_archive_once.yml":
            continue
        workflow = path.read_text(encoding="utf-8")
        assert "secrets." not in workflow, path.name
        assert "FINANCIAL_ARCHIVE_" not in workflow, path.name
        assert "FINANCIAL_PROVIDER_ATTESTATION_KEY" not in workflow, path.name
