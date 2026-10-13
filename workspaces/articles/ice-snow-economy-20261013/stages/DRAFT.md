# DRAFT｜Frozen publication manifest

- task_id: `ice-snow-economy-20261013`
- distribution_mode: `DUAL`
- review_assurance_available: `CHAT_SELF_REVIEW`

## Frozen publication artifacts

- `FINANCE_DEEP`: `publication/FINANCE_DEEP.md`
  - title: **同一个冰雪经济，为什么公司赚的是三种不同的钱？**
  - blob_sha: `79be75d2cfe1a58a30a1a5b547a82d223c168a38`
  - local exact-content Git blob verification: PASS
- `FINANCE_BROAD`: `publication/FINANCE_BROAD.md`
  - title: **3亿人玩冰雪，上市公司为什么不一定更赚钱？**
  - blob_sha: `9aa181f5534cbea111a2cfaa8a7abafa07451da1`
  - local exact-content Git blob verification: PASS

## Deterministic template-scaffolding precheck

The exact Git blob contents were analyzed with deterministic Python regex-family checks before semantic review.

### FINANCE_DEEP
Initial draft showed an over-dense `不是X而是Y / 不只是X而是Y` family: 8 matches. This was treated as a real template cluster and revised rather than waived.

Post-revision counts:
- `不是X而是Y`: 0
- `如果只看`: 1
- `这正是`: 0
- `真正值得/最值得`: 2
- `核心在于`: 0
- `问题在于`: 0
- `值得注意的是`: 0
- `换句话说`: 0
- `所以`: 1

Result: `requires_revise=false` after minimal rewrite. Facts, company coverage, evidence stage and conclusions were preserved.

### FINANCE_BROAD
- `不是X而是Y`: 3
- `如果只看`: 1
- `这正是`: 0
- `真正值得/最值得`: 1
- `核心在于`: 0
- `问题在于`: 0
- `值得注意的是`: 0
- `换句话说`: 0
- `所以`: 2

Result: `requires_revise=false`; no single rhetorical family forms a heavy repeated cluster.

## Frozen-draft invariants

- Every Deep MATERIAL company remains present: **长白山、天府文旅、冰山冷热、雪人集团、三夫户外**.
- Secondary contrast names retained where useful: **西域旅游、探路者**.
- No publication tables.
- `market_explanation_scope=NOT_MATERIAL`; no price-action story or trading instruction inserted.
- Each article contains exactly one final risk paragraph in source Markdown.
- Publication source has no bibliography/source tail; evidence boundary remains in internal research/audit artifacts.

This manifest freezes the two drafts for `EDITORIAL_AUDIT`; later delivery formatting must not silently change analytical content.