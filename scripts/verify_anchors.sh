#!/usr/bin/env bash
set -euo pipefail

index_file="INDEX.md"

if [[ ! -f "$index_file" ]]; then
  echo "ERROR: $index_file not found; cannot verify legacy anchor mappings." >&2
  exit 1
fi

if [[ ! -d archive ]]; then
  echo "Anchor verification skipped: archive/ not present."
  exit 0
fi

archive_files="$(find archive -type f -name "*.md" | sort)"
if [[ -z "${archive_files}" ]]; then
  echo "Anchor verification skipped: no archive markdown files found."
  exit 0
fi

# Extract legacy-style rule IDs (supports single or multi-part prefixes, e.g. RISK_005, WYCKOFF_PHASE_012).
# Prefer ripgrep when a real binary is on PATH; otherwise fall back to grep -E.
# (xargs invokes binaries, not shell functions — an rg shell shim is invisible here,
# and an unguarded `xargs rg … || true` yields an empty ID set and a vacuous pass; see #86.)
id_pattern_pcre='\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_[0-9]{3}\b'
id_pattern_ere='\b[A-Z][A-Z0-9]*(_[A-Z0-9]+)*_[0-9]{3}\b'

set +e
if command -v rg >/dev/null 2>&1; then
  extractor="rg"
  extracted="$(echo "${archive_files}" | xargs rg -No --no-filename "$id_pattern_pcre")"
else
  extractor="grep"
  extracted="$(echo "${archive_files}" | xargs grep -hoE "$id_pattern_ere")"
fi
extract_status=$?
set -e

# xargs: 0 = matches everywhere; 1 (BSD) / 123 (GNU) = some invocation exited 1-125
# (grep/rg "no match" in some files is fine — the empty-extraction check below still
# refuses a run with no IDs at all). Anything else (126/127 command not found, signals)
# is a tool failure — fail loudly instead of proceeding with an empty ID set.
if [[ "$extract_status" -ne 0 && "$extract_status" -ne 1 && "$extract_status" -ne 123 ]]; then
  echo "ERROR: legacy-ID extraction failed (${extractor} via xargs exited ${extract_status}); refusing to report a vacuous pass." >&2
  exit 1
fi

legacy_ids="$(echo "${extracted}" | sort -u | sed '/^$/d')"

if [[ -z "${legacy_ids}" ]]; then
  # The archive has carried legacy rule IDs since v2.3; an empty extraction over a non-empty
  # archive is only reachable through tool failure. Fail loudly rather than pass on nothing.
  echo "ERROR: archive markdown files are present but zero legacy rule IDs were extracted (extractor: ${extractor}); refusing to report a vacuous pass." >&2
  exit 1
fi

missing=""
while IFS= read -r id; do
  if ! grep -Fq -- "$id" "$index_file"; then
    missing="${missing}${id}"$'\n'
  fi
done <<EOF
${legacy_ids}
EOF

if [[ -n "${missing}" ]]; then
  {
    echo "ERROR: Missing legacy rule IDs in $index_file:"
    while IFS= read -r id; do
      [[ -z "$id" ]] && continue
      echo "- $id"
    done <<EOF
${missing}
EOF
  } >&2
  exit 1
fi

legacy_count="$(echo "${legacy_ids}" | wc -l | tr -d ' ')"
echo "Anchor verification passed: ${legacy_count} legacy rule IDs from archive are mapped in $index_file (extractor: ${extractor})."
