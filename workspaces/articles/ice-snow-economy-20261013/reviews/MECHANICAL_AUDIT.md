# MECHANICAL_AUDIT — Dual publication Word QA

- task_id: `ice-snow-economy-20261013`
- stage: `MECHANICAL_AUDIT`
- assurance: `DETERMINISTIC_DOCUMENT_CHECKS + CURRENT_RENDER_VISUAL_INSPECTION`
- review_status: `PASS`

## Immutable article output contract checked
- `FINANCE_DEEP_DOCX`: `ice_snow_economy_deep.docx`
  - sha256: `e863a831a1659b993ee9b46f578d9eb8c70f56ecc1de1b74f1d65a10fdb68922`
  - bytes: `44364`
- `FINANCE_BROAD_DOCX`: `ice_snow_economy_broad.docx`
  - sha256: `10dcfb53e46d629b669045b3f91b1f90169ed47ff4cd168745209ee17ff34895`
  - bytes: `40470`

The article-output set exactly matches DUAL TaskContract article requirements excluding `AUDIT_DOCX`, which is finalized before FINAL_AUDIT terminalization.

## Deterministic checks — Deep
- file exists: PASS
- title centered + 20pt: PASS
- title text preserved; only line wrapping was balanced: PASS
- H1 red + bold, 18pt: PASS
- H2 bold, 15pt: PASS
- H3 bold, 12pt where applicable: PASS
- body 13.5pt: PASS
- legal hierarchy preserved: PASS
- tables: 0
- underlined runs: 0
- publication-tail bibliography/source section: 0
- semantic bold anchors preserved: PASS
- supplied A-share company exact occurrences bold:
  - 长白山 8/8
  - 天府文旅 7/7
  - 冰山冷热 6/6
  - 雪人集团 7/7
  - 三夫户外 6/6
  - 西域旅游 2/2
  - 探路者 3/3
- inline `风险提示：` paragraphs: exactly 1
- risk paragraph fully italic: PASS
- actionable-finance red-line scan: PASS
- rendered pages: 8
- visual inspection of every current rendered page: PASS
- title-wrap fix verification: page 1 reinspected; final pages 2–8 are render-hash-identical to previously inspected current-content pages.

## Deterministic checks — Broad
- file exists: PASS
- title centered + 20pt: PASS
- H1 red + bold, 18pt: PASS
- H2 bold, 15pt where applicable: PASS
- H3 bold, 12pt where applicable: PASS
- body 13.5pt: PASS
- legal hierarchy preserved: PASS
- tables: 0
- underlined runs: 0
- publication-tail bibliography/source section: 0
- semantic bold anchors preserved: PASS
- supplied A-share company exact occurrences bold:
  - 长白山 4/4
  - 天府文旅 3/3
  - 冰山冷热 2/2
  - 雪人集团 3/3
  - 三夫户外 3/3
  - 西域旅游 0/0 (legally omitted under Broad selective compression)
  - 探路者 1/1
- inline `风险提示：` paragraphs: exactly 1
- risk paragraph fully italic: PASS
- actionable-finance red-line scan: PASS
- rendered pages: 4
- visual inspection of every current rendered page: PASS

## Current-render visual QA
All 12 article pages were inspected for the final document versions. No clipping, text overlap, missing glyphs, broken heading hierarchy, isolated one-line title fragment, stale render cache or other pagination defect remained after the Deep title-wrap repair.

## Privacy / delivery boundary
This audit records only public-safe file names and cryptographic hashes. Local runtime paths and render-cache paths are not business-state evidence and are not exposed here.

## Result
`PASS__READY_FOR_FINAL_AUDIT`
