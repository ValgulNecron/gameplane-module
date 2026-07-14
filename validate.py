#!/usr/bin/env python3
"""Gameplane module preflight validator.

Checks every modules/<name>/template.yaml against the ACTUAL OCI image
config of the image(s) it declares (the top-level `spec.image` fallback
plus every `spec.versions[].image` entry), and fails the build on bug
classes that have shipped broken before. Four modules were once authored
and merged without ever being launched against a real cluster; each broke
for a reason that is statically visible in the image's own OCI config:

  1. ARK: Survival Ascended — image has no ENTRYPOINT and its CMD is
     `/bin/bash`. With no TTY that's a non-interactive shell that reads
     EOF on stdin and exits 0 instantly; the pod restart-loops forever
     with an empty log. Fix: `spec.command` must be set whenever an
     image relies on its default CMD being a bare interactive shell.

  2. Project Zomboid — the image is rootless (uid 10000, not the 1000
     its own README claimed). Running it as root, then as the wrong
     non-root uid, both failed. Fix: when the image's own `User` is
     non-root, `spec.security.runAsUser` must be set to match.

  3. Project Zomboid, again — setting `runAsUser` explicitly does not
     give the container the `$HOME` it would have gotten from the
     image's own `USER` directive. SteamCMD then resolved `$HOME/Steam`
     to `//Steam` and died. Fix: whenever the template sets
     `runAsUser`, and the image doesn't bake a `HOME` env var, the
     template must declare one itself.

  4. Garry's Mod / Project Zomboid / 7 Days to Die — `storage.mountPath`
     mounted an empty PVC directly over baked-in image content (the
     directory holding the game's own entrypoint script), so the
     container couldn't even exec. Fix: mountPath must never shadow the
     image's own launcher.

Also checked, cheaply and statically: the declared image actually exists
(three modules once shipped with fabricated image references),
`rcon.protocol` is one of the three values the agent implements, and
`capabilities.mods.loaders` is only meaningful alongside a non-empty
`spec.versions` catalog.

## Design notes on severity (why some checks are WARN, not ERROR)

Every rule below started from a literal reading of the bug report above.
Two were deliberately calibrated DOWN after hand-verifying them against
the four already-fixed modules turned up a false positive:

- Rule 3 (`runAsUser` needs `HOME`) fires as ERROR only when the image
  shows a SteamCMD-shaped signal (an env var or a WorkingDir/Entrypoint/
  Cmd path mentioning "steam"), and WARN otherwise. Verified case: ARK's
  own image (mschnitzer/asa-linux-server) sets `runAsUser: 25000` with
  no baked HOME and no template HOME override, which a literal reading
  would flag — but ARK's `start_server` script (read from the image's
  own GitHub source) never references `$HOME` at all; it hardcodes
  `STEAM_COMPAT_DATA_PATH`/`STEAM_COMPAT_CLIENT_INSTALL_PATH` instead,
  the same substitution SteamCMD-based images use `$HOME` for. Flagging
  it as ERROR would fail CI for a module that has shipped and works.

- Rule 4 (mountPath vs. WorkingDir) treats "mountPath equals the image's
  bare WorkingDir" as WARN, and reserves ERROR for "mountPath is (or is
  an ancestor of) the image's actual Entrypoint/Cmd executable path" —
  the literal repro of the historical bug (mounting over the directory
  that holds entrypoint.sh). Verified case: ARK's WorkingDir is
  `/home/gameserver`, exactly equal to its mountPath — a literal
  equality check would flag it — but the image bakes nothing there at
  build time (a single KIWI-built layer with no COPY of game files;
  everything is fetched by SteamCMD into that empty directory at
  runtime), so mounting a PVC there is exactly correct and is the
  documented, working design. minecraft-java has the identical shape
  (WorkingDir == mountPath == `/data`, also the image's own declared
  Volume) and is likewise fine. The real historical bug (PZ's original
  mountPath of `/home/steam`, see git history) is caught by the
  Entrypoint/Cmd-prefix ERROR check instead, since `/home/steam` is
  literally the parent directory of that image's `entrypoint.sh`.

Both calibrations are documented at the point of use below, with the
verification evidence repeated so a future reader doesn't have to
re-derive it.

## Network resilience

Every image lookup goes through `_curl_json`, which never raises on a
network-level failure (DNS, timeout, connection reset) or on a non-2xx
HTTP status — it returns a tagged failure dict instead. A registry that
can't be reached, or a registry this script doesn't know how to
authenticate against (anything but Docker Hub), is reported as a WARN
and skipped, never a hard failure — only a confirmed 404 (repository or
tag genuinely doesn't exist on Docker Hub) is an ERROR. This means a
transient network blip in CI degrades the run to "couldn't verify",
never a spurious red build.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs pyyaml explicitly
    sys.stderr.write(
        "error: PyYAML is required (`pip install pyyaml`) to run validate.py\n"
    )
    sys.exit(2)

ERROR = "ERROR"
WARN = "WARN"

MANIFEST_ACCEPT = ", ".join(
    [
        "application/vnd.docker.distribution.manifest.v2+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.oci.image.index.v1+json",
    ]
)

CURL_TIMEOUT_SECS = 15

# Wire protocols the agent's rcon package actually implements. Keep in sync with
# the GameTemplate CRD's rcon.protocol enum and agent/internal/rcon/. A protocol
# listed here but not implemented lets a module ship a console that never
# connects, so this list is deliberately conservative.
RCON_PROTOCOLS = ("source", "telnet", "websocket", "battleye", "none")



@dataclass
class Finding:
    level: str
    rule: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.level:5s} [{self.rule}] {self.message}"


# --------------------------------------------------------------------------
# Registry access (Docker Hub only; anything else is skipped gracefully)
# --------------------------------------------------------------------------


def _curl(url: str, headers: dict[str, str] | None = None) -> tuple[int | None, bytes]:
    """Run curl and return (http_status_or_None, body_bytes).

    http_status is None when curl itself failed (DNS, timeout, connection
    reset, TLS error, ...) rather than the server returning a bad status —
    callers use that distinction to tell "confirmed missing" apart from
    "couldn't tell".
    """
    cmd = ["curl", "-s", "-L", "-4", "-m", str(CURL_TIMEOUT_SECS), "-w", "\n%{http_code}"]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    cmd += [url]
    try:
        out = subprocess.run(
            cmd, capture_output=True, timeout=CURL_TIMEOUT_SECS + 10, check=False
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return None, str(exc).encode()
    if out.returncode != 0:
        return None, out.stderr or out.stdout
    body = out.stdout
    idx = body.rfind(b"\n")
    if idx == -1:
        return None, body
    status_bytes = body[idx + 1 :]
    try:
        status = int(status_bytes)
    except ValueError:
        return None, body
    return status, body[:idx]


def _curl_json(url: str, headers: dict[str, str] | None = None):
    """Returns (status, parsed_json_or_None, raw_body)."""
    status, body = _curl(url, headers)
    if status is None:
        return None, None, body
    if status < 200 or status >= 300:
        return status, None, body
    try:
        return status, json.loads(body), body
    except json.JSONDecodeError:
        return status, None, body


def _parse_ref(image_ref: str) -> tuple[str | None, str, str]:
    """Split an image reference into (registry_host_or_None, repo, tag).

    registry_host is None for Docker Hub (bare `user/repo` or official
    `repo`, both normalized to Docker Hub's `library/` namespace).
    """
    if "@" in image_ref:
        # digest reference (repo@sha256:...) — not used by any module today,
        # treat the whole thing after '@' as an opaque tag-equivalent.
        repo_part, tag = image_ref.split("@", 1)
    elif ":" in image_ref.rsplit("/", 1)[-1]:
        repo_part, tag = image_ref.rsplit(":", 1)
    else:
        repo_part, tag = image_ref, "latest"

    first_segment = repo_part.split("/", 1)[0]
    is_custom_registry = "." in first_segment or ":" in first_segment or first_segment == "localhost"
    if is_custom_registry:
        return first_segment, repo_part, tag

    if "/" not in repo_part:
        repo_part = f"library/{repo_part}"
    return None, repo_part, tag


def fetch_image_config(image_ref: str) -> dict[str, Any]:
    """Resolve an image reference to its OCI config, or a tagged failure.

    Return shape: either
      {"ok": True, "config": {...}}
    or
      {"ok": False, "skipped": bool, "network_error": bool, "reason": str}
    """
    registry_host, repo, tag = _parse_ref(image_ref)
    if registry_host is not None:
        return {
            "ok": False,
            "skipped": True,
            "network_error": False,
            "reason": (
                f"registry {registry_host!r} is not Docker Hub — this validator only "
                "knows Docker Hub's anonymous token flow; skipping (not a failure)"
            ),
        }

    token_url = (
        f"https://auth.docker.io/token?service=registry.docker.io"
        f"&scope=repository:{repo}:pull"
    )
    status, token_body, raw = _curl_json(token_url)
    if status is None:
        return {
            "ok": False,
            "skipped": False,
            "network_error": True,
            "reason": f"could not reach auth.docker.io ({raw[:200]!r})",
        }
    if status != 200 or not token_body or "token" not in token_body:
        return {
            "ok": False,
            "skipped": False,
            "network_error": True,
            "reason": f"auth.docker.io returned HTTP {status}",
        }
    token = token_body["token"]
    headers = {"Authorization": f"Bearer {token}", "Accept": MANIFEST_ACCEPT}

    manifest_url = f"https://registry-1.docker.io/v2/{repo}/manifests/{tag}"
    status, manifest, raw = _curl_json(manifest_url, headers)
    if status is None:
        return {
            "ok": False,
            "skipped": False,
            "network_error": True,
            "reason": f"could not reach registry-1.docker.io ({raw[:200]!r})",
        }
    if status == 404:
        return {
            "ok": False,
            "skipped": False,
            "network_error": False,
            "reason": f"{image_ref}: HTTP 404 — repository or tag does not exist on Docker Hub",
        }
    if status != 200 or manifest is None:
        return {
            "ok": False,
            "skipped": False,
            "network_error": True,
            "reason": f"registry returned HTTP {status} resolving the manifest",
        }

    if "manifests" in manifest:  # multi-arch index / manifest list
        chosen = None
        for m in manifest["manifests"]:
            platform = m.get("platform", {})
            if platform.get("architecture") == "amd64" and platform.get("os") == "linux":
                chosen = m
                break
        if chosen is None and manifest["manifests"]:
            chosen = manifest["manifests"][0]
        if chosen is None:
            return {
                "ok": False,
                "skipped": False,
                "network_error": False,
                "reason": f"{image_ref}: manifest list has no platform entries",
            }
        digest = chosen["digest"]
        status, manifest, raw = _curl_json(
            f"https://registry-1.docker.io/v2/{repo}/manifests/{digest}", headers
        )
        if status is None:
            return {
                "ok": False,
                "skipped": False,
                "network_error": True,
                "reason": f"could not reach registry-1.docker.io resolving platform manifest ({raw[:200]!r})",
            }
        if status != 200 or manifest is None:
            return {
                "ok": False,
                "skipped": False,
                "network_error": True,
                "reason": f"registry returned HTTP {status} resolving the platform manifest",
            }

    config_ref = manifest.get("config", {})
    config_digest = config_ref.get("digest")
    if not config_digest:
        return {
            "ok": False,
            "skipped": False,
            "network_error": False,
            "reason": f"{image_ref}: manifest has no config blob reference",
        }
    status, config, raw = _curl_json(
        f"https://registry-1.docker.io/v2/{repo}/blobs/{config_digest}",
        {"Authorization": f"Bearer {token}", "Accept": "*/*"},
    )
    if status is None:
        return {
            "ok": False,
            "skipped": False,
            "network_error": True,
            "reason": f"could not reach registry-1.docker.io fetching the config blob ({raw[:200]!r})",
        }
    if status != 200 or config is None:
        return {
            "ok": False,
            "skipped": False,
            "network_error": True,
            "reason": f"registry returned HTTP {status} fetching the config blob",
        }

    return {"ok": True, "config": config.get("config", {}) or {}}


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def get_path(d: dict, dotted: str):
    cur: Any = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def parse_uid(user_field: str) -> int | None:
    if not user_field:
        return None
    part = user_field.split(":", 1)[0]
    try:
        return int(part)
    except ValueError:
        return None


def image_declares_nonroot(user_field: str | None) -> bool:
    if not user_field:
        return False
    part = user_field.split(":", 1)[0]
    if part == "root":
        return False
    uid = parse_uid(user_field)
    if uid == 0:
        return False
    return True


def _dir_prefix_or_equal(path: str, mount: str) -> bool:
    """True if `path` == mount, or `path` is strictly inside the `mount` dir."""
    if not path or not mount:
        return False
    p = path.rstrip("/")
    m = mount.rstrip("/")
    return p == m or p.startswith(m + "/")


def _steamcmd_shaped(cfg: dict) -> bool:
    for e in cfg.get("Env") or []:
        key = e.split("=", 1)[0].upper()
        if "STEAM" in key:
            return True
    for field in ("WorkingDir",):
        v = (cfg.get(field) or "").lower()
        if "steamcmd" in v:
            return True
    for lst in (cfg.get("Entrypoint") or [], cfg.get("Cmd") or []):
        for tok in lst:
            if "steamcmd" in (tok or "").lower():
                return True
    return False


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------


def rule_no_entrypoint_shell_cmd(spec: dict, cfg: dict, image_ref: str) -> list[Finding]:
    """Rule 1 (ERROR): no ENTRYPOINT + bare shell CMD needs spec.command.

    Historical bug: ARK's image has no ENTRYPOINT and CMD == ["/bin/bash"].
    With no TTY, that's a non-interactive bash that reads EOF on stdin and
    exits 0 immediately — infinite empty-log restart loop.

    Deliberately narrower than "Cmd[0] is a shell binary": `bash script.sh`
    (two-element Cmd, e.g. joedwards32/cs2's `["bash", "entry.sh"]`) is a
    completely normal, working script invocation, not this bug — only a
    *bare* shell with no script argument reproduces the EOF-exit failure,
    so this only fires when len(Cmd) == 1.
    """
    entrypoint = cfg.get("Entrypoint") or []
    cmd = cfg.get("Cmd") or []
    if entrypoint or not cmd:
        return []
    shell_names = {"bash", "sh", "/bin/bash", "/bin/sh"}
    base = cmd[0] or ""
    basename = base.rsplit("/", 1)[-1]
    if len(cmd) == 1 and (base in shell_names or basename in ("bash", "sh")):
        if not spec.get("command"):
            return [
                Finding(
                    ERROR,
                    "no-entrypoint-shell-cmd",
                    f"image {image_ref!r} has no ENTRYPOINT and CMD is bare {cmd!r} — "
                    "a non-interactive container reads EOF on stdin and exits 0 "
                    "instantly (restart-loops with an empty log). spec.command "
                    "MUST be set.",
                )
            ]
    return []


def rule_nonroot_requires_runasuser(spec: dict, cfg: dict, image_ref: str) -> list[Finding]:
    """Rule 2 (ERROR): image's non-root User needs a matching runAsUser.

    Historical bug: Project Zomboid's image is rootless (uid 10000);
    running it as root failed outright.
    """
    user = cfg.get("User") or ""
    if not image_declares_nonroot(user):
        return []
    run_as_user = get_path(spec, "security.runAsUser")
    if run_as_user is None:
        return [
            Finding(
                ERROR,
                "nonroot-user-needs-runasuser",
                f"image {image_ref!r} declares non-root User={user!r} but "
                "spec.security.runAsUser is unset — the container's data "
                "volume needs spec.security.fsGroup too, or the non-root "
                "process can't write to a freshly provisioned PVC.",
            )
        ]
    img_uid = parse_uid(user)
    if img_uid is not None and int(run_as_user) != img_uid:
        return [
            Finding(
                ERROR,
                "runasuser-mismatch",
                f"image {image_ref!r} User={user!r} resolves to uid {img_uid}, "
                f"but spec.security.runAsUser={run_as_user} — these must match "
                "numerically (a wrong-but-nonzero uid fails exactly like the "
                "Project Zomboid uid-1000-vs-10000 bug).",
            )
        ]
    if img_uid is None:
        # A bare name (e.g. "steam") — we cannot resolve the real numeric uid
        # without reading /etc/passwd out of the image's filesystem layers,
        # which this validator deliberately does not do (too expensive for a
        # preflight check). Presence of *some* runAsUser is verified above;
        # the exact value can't be cross-checked statically here.
        pass
    return []


def rule_runasuser_requires_home(spec: dict, cfg: dict, image_ref: str) -> list[Finding]:
    """Rule 3: runAsUser without a HOME (image or template) is risky.

    Historical bug: Project Zomboid set runAsUser but that silently drops
    the $HOME the image's own USER directive would have provided; SteamCMD
    resolved "$HOME/Steam" to "//Steam" and died.

    Severity is calibrated: ERROR only when the image looks SteamCMD-shaped
    (see _steamcmd_shaped and the module docstring for why — ARK sets
    runAsUser with no baked/declared HOME and is provably fine, since its
    start_server script never reads $HOME).
    """
    run_as_user = get_path(spec, "security.runAsUser")
    if run_as_user is None:
        return []
    env_list = cfg.get("Env") or []
    if any(e.split("=", 1)[0] == "HOME" for e in env_list):
        return []
    tmpl_env = spec.get("env") or []
    if any(e.get("name") == "HOME" for e in tmpl_env):
        return []
    steamish = _steamcmd_shaped(cfg)
    level = ERROR if steamish else WARN
    detail = (
        "image looks SteamCMD-shaped (env/paths mention 'steam') — this is "
        "the exact Project Zomboid $HOME/Steam pattern"
        if steamish
        else "no SteamCMD signal detected in this image's static config, so "
        "this is advisory rather than a confirmed repro — a static config "
        "check can't see whether the entrypoint script even reads $HOME"
    )
    return [
        Finding(
            level,
            "runasuser-missing-home",
            f"image {image_ref!r}: spec.security.runAsUser is set, the image "
            f"declares no HOME env, and the template doesn't set one either "
            f"({detail}).",
        )
    ]


def rule_mount_shadowing(spec: dict, cfg: dict, image_ref: str) -> list[Finding]:
    """Rule 4: storage.mountPath must not shadow baked-in image content.

    Historical bug: Garry's Mod / Project Zomboid / 7 Days to Die all
    mounted an empty PVC directly over the directory holding the image's
    own entrypoint script (or its whole game install), so the container
    couldn't exec at all. Project Zomboid's actual original mountPath was
    `/home/steam` — exactly the parent of that image's `entrypoint.sh` —
    confirmed in this repo's git history (commit 64fbf82).

    ERROR: mountPath equals, or is an ancestor directory of, the resolved
    Entrypoint/Cmd executable's absolute path — this is the literal repro
    of the historical bug.

    WARN only: mountPath equals the image's bare WorkingDir. This is
    deliberately not an ERROR — see the module docstring: ARK and
    minecraft-java both have mountPath == WorkingDir == a Volume the image
    declares for exactly this purpose, and are fine. WorkingDir alone
    doesn't tell us whether the image bakes files there; the
    Entrypoint/Cmd-prefix check above is the actual strong signal.

    WARN also: mountPath is a strict ancestor of a declared image Volume
    (not equal to it) — potentially intentional (v-rising covers two
    volumes with one parent-mounted PVC, documented in its template), but
    worth a human glance in case something else under that root is baked.
    """
    mount = get_path(spec, "storage.mountPath")
    if not mount:
        return []
    findings: list[Finding] = []
    entrypoint = cfg.get("Entrypoint") or []
    cmd = cfg.get("Cmd") or []
    exe = entrypoint[0] if entrypoint else (cmd[0] if cmd else None)
    if exe and exe.startswith("/") and _dir_prefix_or_equal(exe, mount):
        which = "Entrypoint" if entrypoint else "Cmd"
        findings.append(
            Finding(
                ERROR,
                "mount-shadows-launcher",
                f"image {image_ref!r}: storage.mountPath={mount!r} would shadow "
                f"the launcher ({which}[0]={exe!r}) — an empty PVC there means "
                "the container can't even exec.",
            )
        )
        return findings  # strongest signal found; skip the weaker checks below

    working_dir = cfg.get("WorkingDir")
    if working_dir and working_dir.rstrip("/") == mount.rstrip("/"):
        findings.append(
            Finding(
                WARN,
                "mount-equals-workingdir",
                f"image {image_ref!r}: storage.mountPath equals the image's "
                f"WorkingDir ({working_dir!r}). Not necessarily a bug (verify "
                "case-by-case whether the image bakes files there at build "
                "time) — confirm before assuming it's safe.",
            )
        )

    for vol in cfg.get("Volumes") or {}:
        if vol.rstrip("/") != mount.rstrip("/") and _dir_prefix_or_equal(vol, mount):
            findings.append(
                Finding(
                    WARN,
                    "mount-is-volume-ancestor",
                    f"image {image_ref!r}: storage.mountPath={mount!r} is an "
                    f"ancestor of declared image volume {vol!r}. Fine if "
                    "covering multiple volumes with one PVC is intentional "
                    "(document it), but confirm nothing else under that root "
                    "is baked content.",
                )
            )
    return findings


def rule_image_exists(image_ref: str, result: dict) -> list[Finding]:
    """Rule 5: the declared image must actually resolve on the registry."""
    if result.get("ok"):
        return []
    if result.get("skipped"):
        return [Finding(WARN, "image-check-skipped", f"{image_ref!r}: {result['reason']}")]
    if result.get("network_error"):
        return [
            Finding(
                WARN,
                "image-check-network-error",
                f"{image_ref!r}: could not verify the image exists ({result['reason']}) "
                "— treated as non-blocking so a registry blip never fails the build.",
            )
        ]
    return [Finding(ERROR, "image-not-found", result["reason"])]


def rule_rcon_protocol(spec: dict) -> list[Finding]:
    """Rule 6: rcon.protocol must be one the agent actually implements."""
    rcon = spec.get("rcon")
    if not rcon:
        return []
    proto = rcon.get("protocol")
    if proto is None:
        # The CRD marks Protocol +kubebuilder:default=source, so an omitted
        # key resolves to "source" at apply time — not a missing/invalid value.
        return []
    if proto not in RCON_PROTOCOLS:
        return [
            Finding(
                ERROR,
                "bad-rcon-protocol",
                f"rcon.protocol={proto!r} is not one of "
                f"{'/'.join(sorted(RCON_PROTOCOLS))} — the agent implements no others.",
            )
        ]
    return []


def rule_mods_loaders_requires_versions(spec: dict) -> list[Finding]:
    """Rule 7: capabilities.mods.loaders needs a non-empty spec.versions."""
    mods = get_path(spec, "capabilities.mods")
    if not mods:
        return []
    loaders = mods.get("loaders")
    if loaders:
        versions = spec.get("versions") or []
        if not versions:
            return [
                Finding(
                    ERROR,
                    "mods-loaders-without-versions",
                    "capabilities.mods.loaders is set but spec.versions is "
                    "empty — no version entry ever selects a loader key, so "
                    "mods silently disable.",
                )
            ]
    return []


def rule_puid_image_needs_fsgroup(spec: dict, cfg: dict, image_ref: str) -> list[Finding]:
    """Rule 8: images with PUID/PGID privilege drop need fsGroup.

    Historical bug: thijsvanloef/palworld-server-docker has User: "" (starts as root)
    but Env declares PUID=1000/PGID=1000, dropping privileges at runtime. Without
    spec.security.fsGroup, the data PVC is root-owned and the dropped-privilege
    user can't write — leading to "PalServer.sh is not executable" and restart loops.

    ERROR: image declares PUID/PGID in Env but template has no fsGroup.
    WARN: template sets runAsUser on a PUID-style image (image needs to start as
    root in order to drop privileges).
    """
    env_list = cfg.get("Env") or []
    has_puid = any(e.split("=", 1)[0] == "PUID" for e in env_list)
    has_pgid = any(e.split("=", 1)[0] == "PGID" for e in env_list)

    if not (has_puid or has_pgid):
        return []

    findings: list[Finding] = []

    # Check if fsGroup is set
    fs_group = get_path(spec, "security.fsGroup")
    if fs_group is None:
        findings.append(
            Finding(
                # WARN, not ERROR. A PUID/PGID image is a *risk* signal, not proof of
                # breakage: many such images chown the volume themselves while still
                # root, before dropping. factorio, rust and terraria all do this and
                # run fine with no fsGroup. But palworld does NOT — once dropped it
                # could not chmod +x the files SteamCMD had just installed
                # ("./PalServer.sh is not executable."), exited 0, and restart-looped
                # 92 times. So: flag it for a human, don't fail the build.
                WARN,
                "puid-image-needs-fsgroup",
                f"image {image_ref!r} declares PUID/PGID in Env (its entrypoint drops "
                "privileges at runtime) but spec.security.fsGroup is unset. If the image "
                "does not chown the data volume before dropping, the dropped user cannot "
                "write its own install — palworld hit exactly this ('./PalServer.sh is not "
                "executable.', exit 0, 92 restarts). Verify, and set spec.security.fsGroup "
                "to the PUID if needed. Do NOT set runAsUser: the image must start as root "
                "in order to drop.",
            )
        )

    # Warn if template incorrectly sets runAsUser on a PUID image
    run_as_user = get_path(spec, "security.runAsUser")
    if run_as_user is not None:
        findings.append(
            Finding(
                WARN,
                "puid-image-with-runasuser",
                f"image {image_ref!r} declares PUID/PGID (needs to start as root "
                "to drop privileges), but spec.security.runAsUser={run_as_user} — "
                "this forces the container to start as non-root, preventing the "
                "privilege-drop mechanism from working. Remove spec.security.runAsUser "
                "and rely on fsGroup for permissions.",
            )
        )

    return findings


def rule_credential_fields_must_be_password(spec: dict) -> list[Finding]:
    """Rule 9: credential-shaped config fields must have type: password.

    Config fields whose names look like credentials (PASSWORD, TOKEN, SECRET,
    etc.) are stored in plaintext in the GameServer CR and etcd if type is not
    'password'. Only 'type: password' stores values in a per-GameServer Secret
    and injects them via SecretKeyRef — the value never lands inline in the CR,
    pod spec, or etcd.

    Historical bug (caught in cs2): SRCDS_TOKEN (a Steam Game Server Login Token)
    was declared as 'type: string', so it would have been stored in plaintext in
    the CR and visible to anyone with kubectl read access.

    ERROR: name looks credential-shaped but type is not 'password'.
    Skip: type is 'bool' or 'int' (a boolean flag named 'PASSWORD_ENABLED' is not
    a credential even if the name matches).
    """
    config_schema = spec.get("configSchema") or []
    findings: list[Finding] = []

    # Credential name patterns to match (case-insensitive)
    credential_substrings = {
        "PASSWORD",
        "PASSWD",
        "PASS",
        "TOKEN",
        "SECRET",
        "APIKEY",
        "API_KEY",
        "AUTHKEY",
        "GSLT",
        "CREDENTIAL",
    }

    for entry in config_schema:
        if not isinstance(entry, dict):
            continue

        name = entry.get("name", "")
        field_type = entry.get("type", "")

        # Skip non-credential types (bool/int are never credentials)
        if field_type in ("bool", "int"):
            continue

        # Check if name contains any credential substring (case-insensitive)
        name_upper = name.upper()
        if any(substring in name_upper for substring in credential_substrings):
            if field_type != "password":
                findings.append(
                    Finding(
                        ERROR,
                        "credential-field-must-be-password",
                        f"config field {name!r} looks credential-shaped but "
                        f"type={field_type!r} (not 'password') — the value will be "
                        "stored in plaintext in the GameServer CR, etcd, and visible "
                        "in 'kubectl get gameserver -o yaml'. Set type: password so "
                        "the operator stores this in a per-GameServer Secret instead.",
                    )
                )

    return findings


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def collect_image_refs(spec: dict) -> list[str]:
    refs: list[str] = []
    if spec.get("image"):
        refs.append(spec["image"])
    for v in spec.get("versions") or []:
        if v.get("image"):
            refs.append(v["image"])
    seen: set[str] = set()
    out: list[str] = []
    for r in refs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def validate_module(spec: dict, cache: dict[str, dict]) -> list[Finding]:
    findings: list[Finding] = []
    image_refs = collect_image_refs(spec)
    if not image_refs:
        return [Finding(ERROR, "no-image", "spec.image is not set")]

    for ref in image_refs:
        if ref not in cache:
            cache[ref] = fetch_image_config(ref)
        findings += rule_image_exists(ref, cache[ref])

    for ref in image_refs:
        result = cache[ref]
        if not result.get("ok"):
            continue
        cfg = result["config"]
        findings += rule_no_entrypoint_shell_cmd(spec, cfg, ref)
        findings += rule_nonroot_requires_runasuser(spec, cfg, ref)
        findings += rule_runasuser_requires_home(spec, cfg, ref)
        findings += rule_mount_shadowing(spec, cfg, ref)
        findings += rule_puid_image_needs_fsgroup(spec, cfg, ref)

    findings += rule_rcon_protocol(spec)
    findings += rule_mods_loaders_requires_versions(spec)
    findings += rule_credential_fields_must_be_password(spec)
    return findings


def discover_modules(root: Path, names: list[str] | None) -> list[Path]:
    if names:
        return [root / n for n in names]
    out = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / "template.yaml").exists():
            out.append(child)
    return out


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent
    names = argv[1:] or None
    module_dirs = discover_modules(root, names)

    cache: dict[str, dict] = {}
    any_error = False
    any_module = False

    clean, warn_only, errored = [], [], []

    for module_dir in module_dirs:
        template_path = module_dir / "template.yaml"
        if not template_path.exists():
            print(f"== {module_dir.name} ==\n  SKIP: no template.yaml\n")
            continue
        any_module = True
        try:
            doc = yaml.safe_load(template_path.read_text())
        except yaml.YAMLError as exc:
            print(f"== {module_dir.name} ==\n  ERROR: could not parse template.yaml: {exc}\n")
            any_error = True
            errored.append(module_dir.name)
            continue
        spec = (doc or {}).get("spec") or {}

        findings = validate_module(spec, cache)
        print(f"== {module_dir.name} ==")
        if not findings:
            print("  OK (no findings)")
            clean.append(module_dir.name)
        else:
            for f in sorted(findings, key=lambda f: (f.level != ERROR, f.rule)):
                print(f"  {f}")
            if any(f.level == ERROR for f in findings):
                any_error = True
                errored.append(module_dir.name)
            else:
                warn_only.append(module_dir.name)
        print()

    print("---")
    print(
        f"SUMMARY: {len(clean)} clean, {len(warn_only)} warn-only, "
        f"{len(errored)} with errors (of {len(module_dirs)} scanned)."
    )
    if errored:
        print("Modules with errors: " + ", ".join(errored))

    if not any_module:
        print("No modules with a template.yaml were found.")
        return 0

    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
