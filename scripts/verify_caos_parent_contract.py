"""Historical CAOS parent conformance checker is retired from active Financial CI.

Standalone Financial must not import, clone or call the external CAOS library.
The old script's implementation is preserved in Git history for provenance.
"""
if __name__ == "__main__":
    raise SystemExit("RETIRED: run scripts/verify_standalone_contract.py instead")
