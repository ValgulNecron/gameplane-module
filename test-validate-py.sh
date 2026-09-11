#!/usr/bin/env bash
# test-validate-py.sh — regression tests for validate.py's directory-layout rules.
#
# Verifies that validate.py enforces README.md, specs.md, and a non-empty samples/
# directory at ERROR severity for allowlisted/enforced modules, and skips non-enforced
# modules.
#
# Run: modules/test-validate-py.sh

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VALIDATE="$HERE/validate.py"
pass=0 fail=0

check() { # check <name> <expected> <actual>
  if [[ "$2" == "$3" ]]; then
    echo "ok   - $1"; pass=$((pass + 1))
  else
    echo "FAIL - $1"; echo "       expected: '$2'"; echo "       actual:   '$3'"; fail=$((fail + 1))
  fi
}

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

create_valid_fixture() {
  local target="$1"
  mkdir -p "$target/samples"
  cat <<'EOF' > "$target/template.yaml"
apiVersion: gameplane.local/v1alpha1
kind: GameTemplate
metadata:
  name: test-module
spec:
  displayName: Test Module
  game: test-game
  version: 1.0.0
  image: alpine:latest
EOF
  echo "# Test Module" > "$target/README.md"
  echo "# Spec" > "$target/specs.md"
  echo "apiVersion: gameplane.local/v1alpha1" > "$target/samples/gameserver.yaml"
}

# 1. Complete module with .layout-enforced passes
MOD="$TMPDIR/valid-mod"
create_valid_fixture "$MOD"
touch "$MOD/.layout-enforced"
out=$(python3 "$VALIDATE" "$MOD" 2>&1) || true
has_layout_err=$(echo "$out" | grep -c "missing-layout-file" || true)
check "complete module passes directory-layout check" "0" "$has_layout_err"

# 2. Missing README.md reports ERROR
MOD="$TMPDIR/missing-readme"
create_valid_fixture "$MOD"
touch "$MOD/.layout-enforced"
rm "$MOD/README.md"
out=$(python3 "$VALIDATE" "$MOD" 2>&1) || true
has_err=$(echo "$out" | grep -c "ERROR \[missing-layout-file\] module is missing README.md" || true)
check "missing README.md reports ERROR [missing-layout-file]" "1" "$has_err"

# 3. Missing specs.md reports ERROR
MOD="$TMPDIR/missing-specs"
create_valid_fixture "$MOD"
touch "$MOD/.layout-enforced"
rm "$MOD/specs.md"
out=$(python3 "$VALIDATE" "$MOD" 2>&1) || true
has_err=$(echo "$out" | grep -c "ERROR \[missing-layout-file\] module is missing specs.md" || true)
check "missing specs.md reports ERROR [missing-layout-file]" "1" "$has_err"

# 4. Missing samples/ directory reports ERROR
MOD="$TMPDIR/missing-samples"
create_valid_fixture "$MOD"
touch "$MOD/.layout-enforced"
rm -rf "$MOD/samples"
out=$(python3 "$VALIDATE" "$MOD" 2>&1) || true
has_err=$(echo "$out" | grep -c "ERROR \[missing-layout-file\] module is missing non-empty samples/ directory" || true)
check "missing samples/ dir reports ERROR [missing-layout-file]" "1" "$has_err"

# 5. Empty samples/ directory reports ERROR
MOD="$TMPDIR/empty-samples"
create_valid_fixture "$MOD"
touch "$MOD/.layout-enforced"
rm -rf "$MOD/samples"/*
out=$(python3 "$VALIDATE" "$MOD" 2>&1) || true
has_err=$(echo "$out" | grep -c "ERROR \[missing-layout-file\] module is missing non-empty samples/ directory" || true)
check "empty samples/ dir reports ERROR [missing-layout-file]" "1" "$has_err"

# 6. Non-allowlisted module without .layout-enforced is exempt from rule
MOD="$TMPDIR/unlisted-mod"
create_valid_fixture "$MOD"
rm "$MOD/specs.md" # missing specs.md, but not allowlisted and no marker
out=$(python3 "$VALIDATE" "$MOD" 2>&1) || true
has_layout_err=$(echo "$out" | grep -c "missing-layout-file" || true)
check "non-enforced module is exempt from layout check" "0" "$has_layout_err"

# 7. Allowlisted slug is enforced without marker file
MOD="$TMPDIR/cs2"
create_valid_fixture "$MOD"
rm "$MOD/specs.md"
out=$(python3 "$VALIDATE" "$MOD" 2>&1) || true
has_err=$(echo "$out" | grep -c "ERROR \[missing-layout-file\] module is missing specs.md" || true)
check "allowlisted module slug (cs2) enforces layout without marker" "1" "$has_err"

echo ""
echo "Summary: $pass passed, $fail failed."
if [ "$fail" -gt 0 ]; then
  exit 1
fi
exit 0
