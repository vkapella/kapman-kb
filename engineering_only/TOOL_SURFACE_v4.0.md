---
system: KapMan
doc_type: reference
kb_version: 4.0.1-alpha
file_last_updated: 2026-08-25
status: draft
tier: T4
---

# TOOL SURFACE

The producer endpoints a session calls directly, the hosts they live on, and how
a session obtains the credential for each. This file owns **transport**: base
URLs, auth mechanism, and credential resolution. It does not own what any
endpoint returns or how a payload is screened — the envelope contract belongs to
`PIPELINE_FEED_VIEW_SPEC_v4.0.md`, the queue contract to
`HITL_QUEUE_CONTRACT_v4.0.md`, and ingest semantics to `PASS1_SCREENING_v4.0.md`
(Operational heuristics).

Skills and runtime files cite this file by section rather than restating it, per
`AGENTS.md` Rule 1 — hosts, credentials, and shell idioms are content that goes
stale, not procedure.

## Contents
- Producer hosts — base URLs, machine auth, credential names
- Credential resolution — the order a session resolves a credential in
- Resolution and use share one shell invocation — the transport hard rule

## Producer hosts

| Producer | Base URL | Machine auth | Credential |
|---|---|---|---|
| kapman-polygon-viewer | `https://kapman-polygon-viewer.fly.dev` | Bearer; explicit GET-only path allowlist | `VIEWER_API_TOKEN` |
| kapman-tradelog | `https://kapman-tradelog.fly.dev` | Bearer; `/api/*` only | `API_BEARER_TOKEN` |

Endpoint paths are named by their owning spec, never here.

The viewer's bearer surface is read-only by construction: the accepted paths are
an explicit allowlist and any non-GET is rejected, so a token cannot trigger a
write or a v2 fan-out (viewer#89, #93, #94).

The tradelog also accepts basic auth (`BASIC_AUTH_USER` / `BASIC_AUTH_PASSWORD`)
on every path, and that is **not** the machine path. Basic auth is the human
browser login: unscoped, and impossible to rotate without also rotating operator
access. Sessions authenticate with `API_BEARER_TOKEN`, which is checked first and
is confined to `/api/*`. `GET /api/health` is unauthenticated by design and is
the correct reachability probe.

## Credential resolution

Resolve in this order, stopping at the first hit:

1. **Already in the environment.** The only path available to a web or mobile
   session: sibling repos arrive there as shallow clones and `.env` is gitignored
   in both producers, so step 2 cannot succeed.
2. **A sibling repo `.env` on disk.** Local checkouts only.
3. **Neither.** Name which of (1) and (2) was checked and why each missed, then
   offer the paste path. Never report this as a generic "fetch unavailable" — the
   operator cannot fix the right layer from a generic failure.

## Resolution and use share one shell invocation

Agent shells do not persist environment between tool calls. Each command runs in
a fresh process, so a credential exported in one call is gone by the next and
`$VAR` expands to empty. A split resolve-then-call sequence returns 401, which
reads as a missing or invalid credential and sends the operator to the wrong
fix entirely — storage, tokens, or sandbox networking — when the credential was
present and readable the whole time.

Resolution and use therefore occupy a single invocation:

    export $(grep -m1 '^VIEWER_API_TOKEN=' "../kapman-polygon-viewer/.env" | xargs) && \
      curl -sS -H "Authorization: Bearer $VIEWER_API_TOKEN" \
      https://kapman-polygon-viewer.fly.dev/api/views

Verified 2026-08-25 against both producers: identical command and credential
returns 200 in one invocation and 401 when split across two.

A credential is referenced as `$VAR` and never written literally into command
text — the permission layer blocks plaintext secrets in commands, and a literal
value lands in the transcript (kb#129).

## Legacy anchors

## Appendix
[content placeholder — to be filled in Claude session]
- PIPELINE_010 -> [content placeholder - to be filled in Claude session]
- PIPELINE_012 -> [content placeholder - to be filled in Claude session]
