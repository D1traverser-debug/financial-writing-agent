"""Autouse test-only provider trust configuration; never used in production."""
import pytest


@pytest.fixture(autouse=True)
def _financial_synthetic_provider_trust(monkeypatch):
    monkeypatch.setenv(
        "FINANCIAL_PROVIDER_ATTESTATION_KEY",
        "test-only-secret-never-deploy-0123456789abcdef0123456789abcdef",
    )
    monkeypatch.setenv("FINANCIAL_TRUSTED_PROVIDER_ID", "synthetic-ci-provider")
    monkeypatch.setenv("FINANCIAL_OWNER_PRINCIPAL", "synthetic-financial-owner")
