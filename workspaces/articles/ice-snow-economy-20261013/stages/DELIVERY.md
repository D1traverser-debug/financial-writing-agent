# DELIVERY — Dual Word artifact evidence

- task_id: `ice-snow-economy-20261013`
- stage: `DELIVERY`
- distribution_mode: `DUAL`
- delivery_channel: `WORD_FILE_ONLY`
- current_session_document_tooling: `AVAILABLE`

## FINANCE_DEEP_DOCX
- file_name: `ice_snow_economy_deep.docx`
- sha256: `e863a831a1659b993ee9b46f578d9eb8c70f56ecc1de1b74f1d65a10fdb68922`
- bytes: `44364`
- publication_source: `workspaces/articles/ice-snow-economy-20261013/publication/FINANCE_DEEP.md`
- publication_source_blob_sha: `79be75d2cfe1a58a30a1a5b547a82d223c168a38`
- rendered_pages: 8
- visual_qa: `PASS__ALL_8_PAGES_INSPECTED_CURRENT_RENDER`
- visual_fix: title line-wrap balanced without changing title text; pages 2–8 were render-hash-identical to the already inspected pre-fix render and final page 1 was reinspected.

## FINANCE_BROAD_DOCX
- file_name: `ice_snow_economy_broad.docx`
- sha256: `10dcfb53e46d629b669045b3f91b1f90169ed47ff4cd168745209ee17ff34895`
- bytes: `40470`
- publication_source: `workspaces/articles/ice-snow-economy-20261013/publication/FINANCE_BROAD.md`
- publication_source_blob_sha: `9aa181f5534cbea111a2cfaa8a7abafa07451da1`
- rendered_pages: 4
- visual_qa: `PASS__ALL_4_PAGES_INSPECTED_CURRENT_RENDER`

## Mechanical checks executed before DELIVERY transition

Both article Word files:
- required artifact exists: PASS
- title 20pt + centered: PASS
- H1 red + bold, 18pt: PASS
- H2 bold, 15pt: PASS
- H3 bold, 12pt where applicable: PASS
- body 13.5pt: PASS
- legal hierarchy preserved: PASS
- publication tables: 0
- underlined runs: 0
- publication-tail source/bibliography heading: 0
- every exact occurrence of supplied A-share company names is bold: PASS
- declared semantic skim-path anchors preserved as bold: PASS
- exactly one final non-empty inline `风险提示：` paragraph: PASS
- complete risk paragraph italic: PASS
- deterministic actionable-finance red-line scan: PASS
- current render visual inspection: PASS

### Company occurrence evidence
Deep:
- 长白山: 8/8 bold
- 天府文旅: 7/7 bold
- 冰山冷热: 6/6 bold
- 雪人集团: 7/7 bold
- 三夫户外: 6/6 bold
- 西域旅游: 2/2 bold
- 探路者: 3/3 bold

Broad:
- 长白山: 4/4 bold
- 天府文旅: 3/3 bold
- 冰山冷热: 2/2 bold
- 雪人集团: 3/3 bold
- 三夫户外: 3/3 bold
- 西域旅游: 0/0 (legally omitted by Broad compression)
- 探路者: 1/1 bold

## Output-contract reconciliation at DELIVERY
Required article outputs under immutable DUAL TaskContract:
- `FINANCE_DEEP_DOCX`: PRESENT + hash-bound
- `FINANCE_BROAD_DOCX`: PRESENT + hash-bound

`AUDIT_DOCX` is intentionally not a DELIVERY article output; it is finalized before bounded FINAL_AUDIT terminalization.

Result: `READY_FOR_GUARDED_DELIVERY_TRANSITION`
