---
name: kapman-screen
description: Load the KapMan v4.0 runtime KB and screen tickers per PASS1_SCREENING
---

Load the full KapMan runtime context and evaluate:

1. Read every file in `llm_runtime/` (all T0–T3 files listed in
   `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md`'s KB file inventory) as
   governing context for this session, in the tier order given there.
2. Execute the **Session entry sequence** from
   `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md` (confirm market date via
   `get_datetime`, detect mode, load journal memory from `kapman-journal/memory/`
   if that repo is attached — announce loaded/empty/not-loaded — then run the
   macro gate) before producing any ticker output.
3. `$ARGUMENTS` may be a plain ticker list, a pasted kapman-polygon-viewer
   Pass 1 export (JSON matching the `A1_FIELDS` contract in `pass1Export.ts`),
   OR a feed + watchlist to fetch (e.g. `swing-long-calls "My Watchlist"`).
   - If it's a pasted export: derive the `VS-YYYYMMDD-HHMM-NN` lineage ID from
     its `exported_at` per `JOURNAL_MGMT_v4.0.md`, echo the ID + `row_count` +
     `as_of` back, and — if `kapman-journal` is attached — write the handoff to
     `handoffs/viewer/<YYYY-MM>/` before screening.
   - If no arguments were given: offer the fetch path (the viewer's export
     API, live since 2026-08-23 — auth via the `VIEWER_API_TOKEN` bearer in
     the viewer repo's local `.env`; paste remains a valid fallback). Fetch
     the watchlists (`GET /api/watchlists`) and views (`GET /api/views`) from
     the viewer, present the export-eligible feed presets as selectable
     options (plus the watchlist when more than one exists), then fetch
     `GET /api/export/pass1?watchlist_id=&view_id=`. The fetched envelope is
     staged and lineage-derived exactly as a pasted one, per
     `KAPMAN_PROJECT_SYSTEM_INSTRUCTIONS_v4.0.md` entry-sequence Stage 4 —
     fetching is a transport, not a trigger; never re-shape a fetched envelope.
   - If tickers/paste/fetch all fail to resolve candidates, ask before
     proceeding.
4. Run `PASS1_SCREENING_v4.0.md` against the resolved candidates and produce
   the report per `REPORT_FORMAT_v4.0.md` / `REPORT_STYLE_v4.0.md`.
5. If `kapman-journal` is attached, log every disposition (Eligible, NO_TRADE,
   WAIT) to `log/pass1/<YYYY-MM>/` and refresh `watchlist.md`, per
   `JOURNAL_MGMT_v4.0.md` — and POST the run's rows to tradelog
   `POST /api/recommendations` per that file's mirror clause (idempotent;
   a failed POST is reported, never blocks). If the journal isn't attached,
   note that logging was skipped this run rather than persisting.
