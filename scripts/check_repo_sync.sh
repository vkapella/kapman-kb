#!/usr/bin/env bash
set -euo pipefail

# Detects the failure class behind #106: work that exists but is invisible from
# the current checkout, so a session confidently asserts a record does not exist.
# It has happened twice — 22 journal files stranded on unmerged claude/* branches
# (recovered 2026-08-13), and a whole Pass 1 + Pass 2 run stranded in an unmerged
# local clone (recovered 2026-08-16). Both repos deliver direct-to-main, so any
# claude/* branch carrying unmerged commits is by definition a delivery failure.
#
# Exits non-zero when anything is stranded, diverged, or could not be checked.
# Override the journal location with KAPMAN_JOURNAL_DIR.

kb_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
journal_dir="${KAPMAN_JOURNAL_DIR:-$(dirname "$kb_dir")/kapman-journal}"

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git not found on PATH; cannot verify repo state." >&2
  exit 1
fi

problems=0
checked=""
skipped=""

check_repo() {
  local label="$1" dir="$2"

  if [[ ! -d "$dir/.git" ]]; then
    # Never silently pass over a repo that was not examined — an unchecked repo
    # is exactly the blind spot this script exists to surface.
    echo "SKIPPED  ${label}: no git repository at ${dir}"
    skipped="${skipped}${label} "
    return 0
  fi

  # A stale remote ref would produce precisely the false negative this check
  # exists to prevent, so a failed fetch is a hard error, not a warning.
  # --prune is load-bearing: without it, remote-tracking refs for branches that
  # were already deleted upstream survive locally and get reported as stranded.
  # First live run of this script did exactly that on two already-deleted refs.
  if ! git -C "$dir" fetch --quiet --prune origin 2>/dev/null; then
    echo "ERROR   ${label}: git fetch failed; refusing to compare against a stale remote ref." >&2
    problems=$((problems + 1))
    return 0
  fi

  local branch counts behind ahead
  branch="$(git -C "$dir" rev-parse --abbrev-ref HEAD)"

  if ! git -C "$dir" rev-parse --verify --quiet origin/main >/dev/null; then
    echo "ERROR   ${label}: origin/main not found after fetch." >&2
    problems=$((problems + 1))
    return 0
  fi

  counts="$(git -C "$dir" rev-list --left-right --count origin/main...HEAD)"
  behind="$(echo "$counts" | cut -f1)"
  ahead="$(echo "$counts" | cut -f2)"

  if [[ "$behind" != "0" || "$ahead" != "0" ]]; then
    echo "DIVERGED ${label}: on '${branch}', ${ahead} ahead / ${behind} behind origin/main"
    [[ "$behind" != "0" ]] && echo "         -> records on origin are NOT visible here; pull before asserting anything is absent"
    [[ "$ahead" != "0" ]] && echo "         -> local work is NOT visible to any other session; push it"
    problems=$((problems + 1))
  fi

  local stranded=""
  while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    local n
    n="$(git -C "$dir" rev-list --count "origin/main..${ref}")"
    if [[ "$n" != "0" ]]; then
      stranded="${stranded}         ${ref} (${n} unmerged)"$'\n'
    fi
  done < <(git -C "$dir" for-each-ref --format='%(refname:short)' 'refs/remotes/origin/claude/*')

  if [[ -n "$stranded" ]]; then
    echo "STRANDED ${label}: claude/* branches carrying commits never merged to main:"
    printf '%s' "$stranded"
    echo "         -> check content before deleting: a branch may hold unrecovered work, or"
    echo "            may be a superseded leftover whose content was re-landed under a new"
    echo "            commit (which 'git cherry' can still report as unmerged)."
    problems=$((problems + 1))
  fi

  local dirty=""
  if [[ -n "$(git -C "$dir" status --porcelain)" ]]; then
    dirty="yes"
    echo "DIRTY    ${label}: uncommitted or untracked changes present"
    problems=$((problems + 1))
  fi

  if [[ "$behind" == "0" && "$ahead" == "0" && -z "$stranded" && -z "$dirty" ]]; then
    echo "OK       ${label}: in sync with origin/main, no stranded branches"
  fi

  checked="${checked}${label} "
}

check_repo "kapman-kb     " "$kb_dir"
check_repo "kapman-journal" "$journal_dir"

echo
if [[ "$problems" -gt 0 ]]; then
  echo "Repo-sync check FAILED: ${problems} condition(s) need attention." >&2
  echo "Per #106: do not assert that a journal record does not exist until these are clear." >&2
  exit 1
fi

echo "Repo-sync check passed for: ${checked:-none}"
if [[ -n "$skipped" ]]; then
  echo "NOT checked (absent): ${skipped}— this pass says nothing about those repos."
fi
