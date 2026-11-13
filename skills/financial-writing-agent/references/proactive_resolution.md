# Financial proactive resolution and evidence recovery

Status: CURRENT_FINANCIAL_OPERATING_RULE
Revision: 1.2
Owner: FINANCIAL_WRITING

## Purpose

Recover what can be recovered before making the user the next dependency. Missing evidence, preference or context is a reason to investigate first—not an automatic reason to stop or ask the user.

## Triggers

Activate this rule when a relevant writing sample or preference is missing, a prior correction/rejection may exist, a previous article may resolve a question, current repository/context/source retrieval may reduce uncertainty, or the assistant is about to ask the user for information it may safely retrieve.

This is not permission to invent facts, preferences, personal history or approval.

## Recovery order

1. Read the exact current article STATE.json and linked artifacts.
2. Inspect Financial-owned approved/edited samples and durable corrections.
3. Inspect prior article outputs and actual acceptance evidence.
4. Use relevant accessible conversation context without asking the user to repeat it.
5. Check current platform, finance-genre and source conventions.
6. Research external practitioner, tool and domain evidence as candidate guidance—not proof of the user's personal voice.
7. Record what was found, what remains uncertain and whether work can continue safely.

Revalidate every time-sensitive or material fact.

## Owner-native record

For article-linked recovery, use `financial_writing_agent.proactive_resolution.record_proactive_resolution_state` to record target, attempted_sources, evidence_refs, outcome, bounded candidate, confidence, contradictions_or_unknowns, validation_plan and safe_to_continue. The resulting execution receipt belongs to the same article state. A RESOLVED or safe PROVISIONAL result should be used to continue, not turned into an unnecessary question.

## Provisional candidates

When evidence is incomplete but safe progress is possible, create a provisional candidate with its scope, evidence, confidence, contradictions and validation plan. For authorial voice, derive only traits supported by actual approved/edited evidence. Keep uncertain traits provisional and test them on real work; do not fall back to generic “humanizer” prose.

## Escalation boundary

Ask the user only when the unresolved choice materially changes the requested outcome, available evidence supports genuinely competing interpretations with no defensible default, proceeding would invent a fact/identity/preference/approval or risky assumption, required evidence remains unavailable after proportionate recovery, or the user explicitly requested confirmation.

Ask one focused question, not a questionnaire. Do not ask merely because the best evidence is imperfect.

## Problem-response integration

For a repairable defect, do not stop at a recommendation. Continue:
`recover evidence → diagnose local and systemic causes → challenge assumptions → research alternatives → choose a bounded repair → execute → read back → test negative and valid-neighbor cases → observe the result`.

A local symptom fix is not complete until the shared cause and downstream effects have been checked.

## Logging and assurance

Record material problems and system effects in Financial's evolution evidence. Small/local issues may use a compact entry; repeated, user-rejected or architectural issues require the full causal chronology, alternatives, tests, result and remaining unknowns.

Rule text is DECLARED. Passing owner-native behavior and trajectory tests supports EXECUTABLE_POLICY_AND_TRAJECTORY_VERIFIED. LIVE_OUTCOME_VERIFIED requires real Financial work and observed user/reader outcomes.
