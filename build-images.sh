#!/usr/bin/env bash
# build-images.sh — build, push, and sign Gameplane-owned container images.
#
# Builds purpose-built Dockerfiles for games requiring auxiliary service
# supervision (FR-012) or non-crashing diagnostic idle for missing tokens (FR-013):
#   - fivem (txAdmin + embedded database)
#   - farming-simulator-25 (headless Wine + dummy X11 + web admin portal)
#   - euro-truck-simulator-2 (ETS2 server logon token diagnostic idle)
#   - beammp (BeamMP auth key diagnostic idle)
#
# Usage:
#   modules/build-images.sh build                                       # build all 4 images locally
#   modules/build-images.sh build --name fivem                          # build only fivem
#   modules/build-images.sh push --registry ghcr.io/valgulnecron/gameplane --sign

set -euo pipefail

KNOWN_IMAGES=("fivem" "farming-simulator-25" "euro-truck-simulator-2" "beammp")

usage() {
  cat <<USAGE
Usage: $0 <build|push> [flags]

Commands:
  build              Build container images locally
  push               Build and push container images to an OCI registry

Flags:
  --registry <ref>   Registry prefix (e.g. ghcr.io/valgulnecron/gameplane) [required for push]
  --name <name>      Target a specific image (fivem, farming-simulator-25, euro-truck-simulator-2, beammp)
  --tag <tag>        Override image tag (default: latest or module version)
  --sign             cosign-sign each pushed image by manifest digest
  --plain-http       Use plain HTTP (for local testing registries)
  --insecure         Skip TLS verification
  --tlog-upload      Record signature in public Rekor transparency log (default: offline)
USAGE
}

ACTION="${1:-}"
[[ -n "$ACTION" ]] || { usage; exit 1; }
shift

REGISTRY=""
TARGET=""
OVERRIDE_TAG=""
SIGN=0
PLAIN_HTTP=""
INSECURE=""
TLOG_UPLOAD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --registry)    REGISTRY="$2"; shift 2 ;;
    --name)        TARGET="$2"; shift 2 ;;
    --tag)         OVERRIDE_TAG="$2"; shift 2 ;;
    --sign)        SIGN=1; shift ;;
    --plain-http)  PLAIN_HTTP=1; shift ;;
    --insecure)    INSECURE=1; shift ;;
    --tlog-upload) TLOG_UPLOAD=1; shift ;;
    -h|--help)     usage; exit 0 ;;
    *)             echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$ACTION" == "push" ]] && [[ -z "$REGISTRY" ]]; then
  echo "Error: --registry is required for push" >&2
  exit 1
fi

build_and_push() {
  local name="$1"
  local dir="$SCRIPT_DIR/$name"

  if [[ ! -f "$dir/Dockerfile" ]]; then
    echo "Skipping $name: no Dockerfile found at $dir/Dockerfile" >&2
    return 0
  fi

  local version="latest"
  if [[ -n "$OVERRIDE_TAG" ]]; then
    version="$OVERRIDE_TAG"
  elif [[ -f "$dir/module.yaml" ]] && command -v python3 >/dev/null 2>&1; then
    local v
    v="$(python3 -c "import yaml; print(yaml.safe_load(open('$dir/module.yaml'))['version'])" 2>/dev/null || true)"
    [[ -n "$v" ]] && version="$v"
  fi

  local image_tag="gameplane-$name:$version"
  if [[ -n "$REGISTRY" ]]; then
    image_tag="$REGISTRY/$name:$version"
  fi

  echo "==> Building $image_tag from $dir/Dockerfile"
  docker build -t "$image_tag" -f "$dir/Dockerfile" "$dir"

  if [[ "$ACTION" == "push" ]]; then
    echo "==> Pushing $image_tag"
    docker push "$image_tag"

    if (( SIGN )); then
      local digest
      digest="$(docker inspect --format='{{index .RepoDigests 0}}' "$image_tag" 2>/dev/null | grep -o 'sha256:[a-f0-9]*' || true)"
      if [[ -z "$digest" ]]; then
        echo "Error: could not determine digest for $image_tag" >&2
        return 1
      fi

      echo "==> Signing $REGISTRY/$name@$digest"
      local sargs=( sign --key env://COSIGN_PRIVATE_KEY --yes
                    --new-bundle-format=false --use-signing-config=false )
      if (( TLOG_UPLOAD )); then
        echo ">> (recording signature in public Rekor transparency log)"
      else
        sargs+=( --tlog-upload=false )
      fi
      [[ -n "$PLAIN_HTTP" ]] && sargs+=( --allow-http-registry )
      [[ -n "$INSECURE" ]] && sargs+=( --allow-insecure-registry )
      cosign "${sargs[@]}" "$REGISTRY/$name@$digest"
    fi
  fi
}

TARGETS=("${KNOWN_IMAGES[@]}")
if [[ -n "$TARGET" ]]; then
  TARGETS=("$TARGET")
fi

for img in "${TARGETS[@]}"; do
  build_and_push "$img"
done

echo "==> Done."
