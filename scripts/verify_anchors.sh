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
legacy_ids="$(echo "${archive_files}" | xargs rg -No --no-filename '\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*_[0-9]{3}\b' | sort -u || true)"
if [[ -z "${legacy_ids}" ]]; then
  echo "Anchor verification passed: no legacy rule IDs found in archive markdown files."
  exit 0
fi

missing=""
while IFS= read -r id; do
  if ! rg -Fq -- "$id" "$index_file"; then
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
echo "Anchor verification passed: ${legacy_count} legacy rule IDs from archive are mapped in $index_file."
