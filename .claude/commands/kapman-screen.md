---
description: Load the KapMan v4.0 runtime KB and screen tickers per PASS1_SCREENING
---

Load the full KapMan runtime context and evaluate: $ARGUMENTS

1. Read every file in `llm_runtime/` (all T0–T3 files listed in
   `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md`'s KB file inventory) as
   governing context for this session, in the tier order given there.
2. Execute the **Session entry sequence** from
   `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md` (confirm market date via
   `get_datetime`, detect mode, load journal memory from `kapman-journal/memory/`
   if that repo is attached — announce loaded/empty/not-loaded — then run the
   macro gate) before producing any ticker output.
3. `$ARGUMENTS` may be a plain ticker list, OR a pasted kapman-polygon-viewer
   Pass 1 export (JSON matching the `A1_FIELDS` contract in `pass1Export.ts`).
   - If it's a pasted export: derive the `VS-YYYYMMDD-HHMM-NN` lineage ID from
     its `exported_at` per `JOURNAL_MGMT_v4.0.md`, echo the ID + `row_count` +
     `as_of` back, and — if `kapman-journal` is attached — write the handoff to
     `handoffs/viewer/<YYYY-MM>/` before screening.
   - If neither tickers nor a pasted export were given, ask before proceeding.
4. Run `PASS1_SCREENING_v4.0.md` against the resolved candidates and produce
   the report per `REPORT_FORMAT_v4.0.md` / `REPORT_STYLE_v4.0.md`.
5. If `kapman-journal` is attached, log every disposition (Eligible, NO_TRADE,
   WAIT) to `log/pass1/<YYYY-MM>/` and refresh `watchlist.md`, per
   `JOURNAL_MGMT_v4.0.md`. If it isn't attached, note that logging was skipped
   this run rather than persisting.
