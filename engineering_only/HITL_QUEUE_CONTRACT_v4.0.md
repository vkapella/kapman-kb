---
system: KapMan
doc_type: reference
kb_version: 4.0.1
file_last_updated: 2026-08-23
status: active
tier: —
---

# HITL QUEUE CONTRACT

## Purpose

This file is the code-facing contract between the KapMan runtime and the
Tradelog Today review queue for a judgment-bearing proposal whose operator
response may occur outside the conversation that produced it (kb#124).

`WYCKOFF_v4.0.md` owns the behavioral rule: confirmation state never crosses a
session boundary; the receiving session begins at `UNKNOWN`; current data and
current gates run first; and a materially changed proposal is returned to the
operator rather than silently applied. This file does not restate those gates,
their thresholds, or their behavioral consequences.

This file owns the machine-readable queue-item, proposal-snapshot, declaration,
comparison, idempotency, and fresh-run-outcome grammar that Tradelog Increment 2
will implement. A proposal snapshot records what the operator reviewed. It is
historical input, never current market data or current Wyckoff authority.

The initial scope is `WYCKOFF_FLAGGED` only. Generic queue vocabulary does not
authorize additional proposal kinds. Portfolio hold, close, or restructure
declarations require their own approved behavioral contract before they can use
this grammar.

## Authority boundaries

| Concern | Owner |
|---|---|
| Session start at `UNKNOWN`; validity, confidence-tier, force-flag, and freshness behavior; `pipeline-accepted`, `declared`, and `pipeline-flagged` semantics | `llm_runtime/WYCKOFF_v4.0.md` |
| Exact queue-item, proposal-snapshot, declaration, comparison, idempotency, and outcome shapes | This file |
| Current viewer reading supplied to the fresh run | KapMan viewer export |
| Persistence, display, and transport of queue items, declarations, and outcomes | Tradelog Today queue |
| Journal staging of each declaration a run consumed | `llm_runtime/JOURNAL_MGMT_v4.0.md` (`handoffs/queue/`, kind `queue_declaration`) — the journal remains the record of authority; a run must be auditable from the journal alone |
| Whether and when a fresh run occurs | Operator only |
| Broker action or order execution | None |

Tradelog is the queue record and transport plane; it is not the authority for
the current Wyckoff reading. A declaration is an operator statement tied to one
reviewed proposal. It is not confirmation, recommendation approval, execution
authorization, or a broker instruction.

No endpoint name or transport capability is active merely because it appears
in a proposed implementation. Endpoint names enter this contract only after the
corresponding Tradelog surface exists and has been verified. Until then, the
contract defines record semantics and shapes, not a callable capability.

If this file and `WYCKOFF_v4.0.md` disagree about behavioral meaning, WYCKOFF
wins. If implementation code disagrees with this file's record grammar, this
file wins until the contract is deliberately revised.

## Queue item and immutable proposal snapshot

A queue item is the immutable record of one proposal presented for later
operator review. Tradelog never edits the proposal to reflect a declaration,
fresh run, or outcome. Those are separate records linked by `queue_item_id`.

Queue status is therefore derived from related declaration and outcome records;
it is not mutable state stored on the queue item.

### Queue-item grammar

| Field | Type | Required | Contract |
|---|---|---:|---|
| `queue_schema_version` | string | yes | Queue-contract namespace, independent of KB and viewer schema versions |
| `queue_item_id` | string | yes | Globally unique, stable across delivery retries, minted by the producing run and treated as opaque by Tradelog |
| `kind` | enum | yes | `WYCKOFF_FLAGGED` only in this contract version |
| `created_at` | ISO-8601 datetime with offset | yes | Time the producing run created the queue item |
| `source` | object | yes | Source lineage described below |
| `ticker` | string | yes | Uppercase ticker that the proposal concerns |
| `proposal_snapshot` | object | yes | Exact reviewed proposal grammar below |
| `proposal_hash` | string | yes | Integrity identity for `proposal_snapshot`; construction is owned by the integrity section below |

`queue_item_id` is the idempotency key. Re-delivery of the same ID with the
same `proposal_hash` is a no-op. Re-delivery of the same ID with a different
hash is a contract conflict and must be rejected; it is never an update.

### Source lineage

| Field | Type | Required | Contract |
|---|---|---:|---|
| `lineage_id` | string | yes | Viewer handoff lineage that supplied the reviewed row |
| `rec_id` | string or null | yes | Pass-1 recommendation ID when one exists; explicit null when the proposal preceded recommendation creation |
| `exported_at` | ISO-8601 datetime with offset | yes | Echoed from the viewer export; never replaced with queue creation time |
| `as_of` | `YYYY-MM-DD` | yes | Market-data date represented by the reviewed proposal |
| `viewer_schema_version` | string or null | yes | Echoed when supplied; null when the source envelope did not provide it |

The queue does not mint or repair source lineage. A malformed or missing
`lineage_id` rejects the item. Null `rec_id` or `viewer_schema_version` remains
null and is never synthesized.

### Proposal-snapshot grammar

| Field | Type | Required | Contract |
|---|---|---:|---|
| `proposal_status` | literal | yes | Historical value `pipeline-flagged`; it does not become current-session status later |
| `operator_prompt` | string | yes | Exact proposal and options shown to the operator, not a reconstructed summary |
| `decision_inputs` | object | yes | Exact source values used by the producing run, preserving absent keys and explicit nulls |
| `evaluation` | object | yes | The producing run's gate result and named reasons |

`decision_inputs` may contain the following viewer fields:

- `regime`
- `phase`
- `regime_confidence`
- `phase_confidence`
- `last_event`
- `last_event_date`
- `setup_tags`
- `weekly_agrees`
- `structure_conflict`
- `as_of`
- `data_through`

The object preserves the source's three distinct states:

- Key present with a value
- Key present with `null`
- Key absent

The producer and Tradelog must not insert defaults, convert absence to null, or
drop null-valued keys. Additional viewer fields may ride in
`decision_inputs`, but their presence does not make them decision-bearing
without a contract revision.

`evaluation` contains:

| Field | Type | Required | Contract |
|---|---|---:|---|
| `gating_confidence` | number or null | yes | Value used by the producing run; null when it could not be computed |
| `gate_result` | literal | yes | `pipeline-flagged` |
| `flag_reasons` | string array | yes | Non-empty named reasons surfaced to the operator |
| `freshness_valid` | boolean | yes | Whether the reviewed source passed the producing run's freshness check |

The proposal snapshot records exactly what was reviewed and why it was flagged.
It is never refreshed in place. A later viewer envelope belongs to the fresh
run and is stored only on that run's outcome record.

## Declaration grammar

| Field | Type | Required | Contract |
|---|---|---:|---|
| `queue_schema_version` | string | yes | Same namespace as the queue item |
| `declaration_id` | string | yes | Globally unique, minted by Tradelog at resolution |
| `queue_item_id` | string | yes | The reviewed proposal |
| `proposal_hash` | string | yes | Echoed from the queue item **as the operator saw it**; a mismatch against the queue item's stored hash rejects the declaration — tamper evidence, never repaired |
| `statement` | enum | yes | `ACCEPT` \| `OVERRIDE` \| `ESTIMATE` \| `DEFER` — behavioral meaning owned by WYCKOFF's queued-declaration rule; the vocabulary is pinned here |
| `override_reading` | object or null | yes | Non-null **iff** `statement = OVERRIDE`: `{regime, phase or null}` drawn from WYCKOFF's canonical vocabulary; null otherwise. `ACCEPT` accepts the snapshot's proposed reading — it never carries a different one |
| `operator_note` | string or null | yes | Verbatim free text; never parsed for semantics |
| `stated_at` | ISO-8601 datetime with offset | yes | When the operator resolved the card |

Multiple declarations for one queue item: all are retained append-only; the
consuming run uses the one with the latest `stated_at` and records the others
as superseded history. A declaration is consumed at most once — after a
fresh-run outcome exists for the pair, later runs treat the queue item as
resolved.

## Material-comparison grammar

The fresh run compares its current viewer reading against `proposal_snapshot`
over a **fixed decision-bearing field list** — never over whatever fields
happen to exist, so envelope evolution cannot manufacture divergence:

`regime`, `phase`, `last_event`, `setup_tags`, `weekly_agrees`,
`structure_conflict`, the gate outcome, the `flag_reasons` set, and
`freshness_valid`.

Divergence rules:

- Any value change in a listed field diverges, with key-present-with-value,
  key-present-with-null, and key-absent treated as three distinct states.
- `flag_reasons` compares as a set (order-insensitive).
- `gating_confidence` diverges only when it **crosses a gate boundary**
  (`τ_low` / `τ_high`, consumed by name per SYSTEM_PARAMS), not on any tick.
- The comparison verdict is `{matches: boolean, diverged_fields: [names]}`.

**No declaration TTL in this contract version — deliberately.** Divergence does
the aging work: a stale proposal diverges naturally, and a proposal still
materially true is still answerable. This implements WYCKOFF's "staleness makes
it more likely to be returned, not less."

## Fresh-run outcome record

| Field | Type | Required | Contract |
|---|---|---:|---|
| `outcome_id` | string | yes | Globally unique |
| `queue_item_id` | string | yes | Join key |
| `declaration_id` | string or null | yes | Null when the run consumed the item with no declaration present |
| `consumed_at` | ISO-8601 datetime with offset | yes | When the fresh run evaluated the item |
| `consuming_lineage_id` | string | yes | The consuming run's lineage |
| `comparison` | object | yes | The material-comparison verdict verbatim |
| `resolution` | enum | yes | `PIPELINE_ACCEPTED_FRESH` \| `DECLARED_ACCEPT` \| `DECLARED_OVERRIDE` \| `ESTIMATION_PATH` \| `DEFERRED` \| `RETURNED_DIVERGED` |
| `resulting_status` | string | yes | The WYCKOFF status the ticker ended the session with |

Record semantics only: how Tradelog receives an outcome is defined when the
Increment-2 endpoints exist and have been verified, per the endpoint rule in
the authority boundaries above.

## Verified Tradelog surfaces (registered 2026-08-23)

Per the endpoint rule above, these names entered the contract only after the
surfaces were deployed (tradelog#329, commit 1822b56) and live-verified on
2026-08-23 (empty-list reads, named-issue validation rejections, and the full
13-step contract round-trip exercised pre-deploy on the identical build).
Base: the kapman-tradelog app; auth: the app's basic-auth credentials.

| Surface | Verb + path | Contract role |
|---|---|---|
| Submit a queue item | `POST /api/queue/items` | Producer delivery; idempotent per the queue-item grammar (duplicate no-op, hash conflict 409, hash verified against the snapshot at ingest 422) |
| List queue items | `GET /api/queue/items?status=&ticker=&lineageId=` | Display / audit; status is derived (`PENDING` / `DECLARED` / `CONSUMED`) |
| Record a declaration | `POST /api/queue/items/{queue_item_id}/declarations` | Operator resolution from the Today screen; hash echo enforced 422; refused 409 once consumed |
| Fetch pending declarations | `GET /api/queue/pending-declarations` | What a fresh run consumes: DECLARED items with the verbatim snapshot + effective (latest `stated_at`) declaration |
| Report a fresh-run outcome | `POST /api/queue/outcomes` | Consumes the item; one outcome per item (duplicate no-op, second outcome 409) |

## Integrity and idempotency

`proposal_hash` is the lowercase-hex SHA-256 digest of the **RFC 8785 (JCS)
canonical JSON** serialization of `proposal_snapshot`. Tradelog stores and
redelivers the snapshot bytes verbatim; consumers verify by recomputing the
digest over the delivered canonical form and comparing hash strings for
equality — never by semantic re-derivation. The implementation ships in
Increment-2 code with golden tests against worked examples added to this file
at that time (the same discipline as `TICKET_BROKER_MAPPING_v4.0.md`: no code
before a testable surface exists).
