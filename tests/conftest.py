"""Autouse test-only provider trust configuration; never used in production."""
import pytest


@pytest.fixture(autouse=True)
def _financial_synthetic_provider_trust(monkeypatch):
    monkeypatch.setenv(
        "FINANCIAL_PROVIDER_ATTESTATION_KEY",
        "test-only-secret-never-deploy-0123456789abcdef0123456789abcdef",
    )
    monkeypatch.setenv("FINANCIAL_TRUSTED_PROVIDER_ID", "synthetic-financial-provider")
    monkeypatch.setenv("FINANCIAL_OWNER_PRINCIPAL", "synthetic-financial-owner")
    monkeypatch.setenv("FINANCIAL_CI_ATTESTATION_KEY", "synthetic-ci-key-never-deploy-0123456789abcdef0123456789abcdef")
    monkeypatch.setenv("FINANCIAL_CI_PROVIDER_ID", "synthetic-ci-provider")
    monkeypatch.setenv("FINANCIAL_INDEPENDENT_REVIEW_KEY", "synthetic-review-key-never-deploy-0123456789abcdef0123456789abcdef")
    monkeypatch.setenv("FINANCIAL_INDEPENDENT_REVIEW_PROVIDER_ID", "synthetic-independent-review-provider")
