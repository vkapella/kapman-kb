#!/usr/bin/env bash
set -euo pipefail

required=(system doc_type kb_version file_last_updated status tier)
failed=0

check_file() {
  local f="$1"
  local content
  content=$(sed -n '1,80p' "$f")

  if [[ "$content" != ---$'\n'* ]]; then
    echo "ERROR: missing frontmatter start in $f"
    failed=1
    return
  fi

  # Limit scan to frontmatter block only.
  local fm
  fm=$(awk 'NR==1 && $0=="---" {inside=1; next} inside && $0=="---" {exit} inside {print}' "$f")

  if [[ -z "$fm" ]]; then
    echo "ERROR: empty frontmatter in $f"
    failed=1
    return
  fi

  for key in "${required[@]}"; do
    if ! grep -Eq "^${key}:[[:space:]]*.+$" <<<"$fm"; then
      echo "ERROR: missing '${key}' in $f"
      failed=1
    fi
  done
}

for f in llm_runtime/*.md engineering_only/*.md; do
  [[ -f "$f" ]] || continue
  check_file "$f"
done

if [[ $failed -ne 0 ]]; then
  exit 1
fi

echo "Frontmatter verification passed."
