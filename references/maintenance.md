# Maintenance module

New feedback must be classified before changing the system.

- A run-local constraint belongs only to the current TaskContract/state.
- A durable writing rule updates its single owner in `config/rule_ownership.json`.
- A platform observation is an experience sample until repeated evidence supports a stronger rule.
- If an existing rule was skipped, treat it as a runtime/trajectory defect; do not duplicate the rule in more files.
- External platform changes require fresh authoritative verification before policy changes.

## Change protocol

1. Identify the rule owner and affected runtime stages.
2. Modify the owner only.
3. Search for contradictory or duplicate legacy wording.
4. Add or update regression tests and trajectory assertions.
5. Run unit, static and trajectory tests.
6. Run a representative live writing task when behavior depends on model/tool execution.
7. Promote the change only after readback and regression pass.

A documentation edit is not proof that an Agent will execute the behavior. Runtime traces and outputs are the evidence.
