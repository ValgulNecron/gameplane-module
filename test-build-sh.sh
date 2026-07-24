#!/usr/bin/env bash
# test-build-sh.sh — regression tests for build.sh's signing preconditions.
#
# Focus: the manifest-digest parser. `--sign` signs whatever digest this parser
# returns, and that code path only ever runs in the release/republish
# workflows — so a mistake there would sign the wrong object in production with
# nothing to catch it. These tests need no registry and no cosign.
#
# Run: modules/test-build-sh.sh

set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/build.sh"
pass=0 fail=0

check() { # check <name> <expected> <actual>
  if [[ "$2" == "$3" ]]; then
    echo "ok   - $1"; pass=$((pass + 1))
  else
    echo "FAIL - $1"; echo "       expected: '$2'"; echo "       actual:   '$3'"; fail=$((fail + 1))
  fi
}

MANIFEST="sha256:391f362c54183cd0528018d0576089e1fa76258b9f337ee6d525a17d6e8f6f3e"
LAYER="sha256:4b2b418bbeeb1f1d0d3e1a0f4a5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e"

# 1. Real oras output shape (layer digests abbreviated, authoritative Digest: line).
out="$(cat <<EOF
Preparing module.yaml
Uploading 4b2b418bbeeb README.md
Uploaded  93f94724572f module.yaml
Pushed [registry] localhost:5001/testmod:1.0.0
ArtifactType: application/vnd.gameplane.module.v1+json
Digest: $MANIFEST
EOF
)"
check "parses the manifest digest from real oras output" \
  "$MANIFEST" "$(printf '%s\n' "$out" | "$BUILD" _parse-digest)"

# 2. THE REGRESSION: an oras that prints FULL layer digests before the summary.
#    The old parser (first sha256 token anywhere) returned the LAYER digest here
#    and would have signed the wrong object. Current oras abbreviates layer
#    digests, so only a synthetic fixture can pin this behaviour down.
out="$(cat <<EOF
Uploading $LAYER README.md
Uploaded  $LAYER README.md
Pushed [registry] localhost:5001/testmod:1.0.0
Digest: $MANIFEST
EOF
)"
got="$(printf '%s\n' "$out" | "$BUILD" _parse-digest)"
check "ignores full layer digests printed before the summary line" "$MANIFEST" "$got"
check "does not return the layer digest" "no" "$([[ "$got" == "$LAYER" ]] && echo yes || echo no)"

# 3. Malformed/short digests must not match (fail loudly rather than sign junk).
check "rejects a short hash" "" "$(printf 'Digest: sha256:abc123\n' | "$BUILD" _parse-digest)"
check "rejects a non-anchored sha256 mention" "" \
  "$(printf 'note: see %s for details\n' "$MANIFEST" | "$BUILD" _parse-digest)"
check "returns empty when no digest is present" "" \
  "$(printf 'Pushed something\nNo digest here\n' | "$BUILD" _parse-digest)"

# 4. Leading whitespace / CRLF tolerance (oras output has gone through pipes).
check "tolerates leading whitespace" "$MANIFEST" \
  "$(printf '   Digest: %s\n' "$MANIFEST" | "$BUILD" _parse-digest)"

# 5. Flag guards.
"$BUILD" push --registry localhost:5001 --tlog-upload >/dev/null 2>&1
check "--tlog-upload without --sign exits 2" "2" "$?"

echo
echo "passed: $pass  failed: $fail"
[[ $fail -eq 0 ]]
