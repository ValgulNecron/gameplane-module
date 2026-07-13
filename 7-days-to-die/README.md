# `7-days-to-die` module

Gameplane GameTemplate for 7 Days to Die dedicated servers.

## Install

```sh
kubectl apply -f modules/7-days-to-die/template.yaml
```

## Image

[`vinanrra/7dtd-server`](https://github.com/vinanrra/Docker-7DaysToDie), a
[LinuxGSM](https://linuxgsm.com/)-based wrapper. Its Dockerfile declares
**five separate volumes**, none nested inside another:

| Path | Holds |
| --- | --- |
| `/home/sdtdserver/.local/share/7DaysToDie/` | World saves ("where maps are stored") |
| `/home/sdtdserver/serverfiles/` | Server install, `Mods/`, `serverconfig.xml` |
| `/home/sdtdserver/log/` | Server logs |
| `/home/sdtdserver/lgsm/backup/` | LinuxGSM's own backups |
| `/home/sdtdserver/lgsm/config-lgsm/sdtdserver/` | LinuxGSM wrapper config |

Gameplane mounts exactly one PVC per GameServer. These five directories
don't share a safe common ancestor — the ENTRYPOINT script (`user.sh`) and
the LinuxGSM checkout are baked directly under `/home/sdtdserver`, a
sibling of all five, so mounting the parent shadows the entrypoint itself
and the container won't start at all.

## Storage — why only world saves persist

`storage.mountPath` is `/home/sdtdserver/.local/share/7DaysToDie` — world
saves only. This was the actual bug being fixed here: the previous
template mounted `/home/sdtd/server`, a path that doesn't exist in this
image at all, so the PVC bound to nothing, the world lived on the
container's ephemeral layer, and it was destroyed on every restart while
backups silently snapshotted an empty directory.

Given Gameplane's one-PVC-per-server model can't cover all five volumes,
world saves won this trade-off deliberately: losing player-built worlds on
every restart is destructive and irreversible, while the server
reinstalling itself (`serverfiles/`) on every restart is slow and
bandwidth-wasteful but not destructive — LinuxGSM's `install.sh` already
detects a missing `serverfiles/DONT_REMOVE.txt` and reinstalls
automatically, so it recovers on its own.

**Consequence: `serverconfig.xml` (server name, max players, difficulty,
PVP, etc.) lives under `serverfiles/`, which is not on the persisted
volume.** There is no configSchema for in-game server settings in this
template because there's nowhere on the persisted mount to render them —
this image documents no env-var mechanism for any of them either (the
README says outright: "If you want to change any server settings, edit
`/path/to/ServerFiles/sdtdserver.xml`"). Settings reset to the image's
defaults on every restart unless you fork this template with a different
storage trade-off.

## Console & RCON — intentionally disabled

`rcon: { protocol: none }`, deliberately. 7 Days to Die's console is
telnet on port 8081 (declared in `ports[]` even though unused, matching
the image's own docs), and the CRD's `RCONSpec` supports it
(`protocol: telnet`). The blocker is the password: 7 Days to Die keeps
`TelnetPassword` in `serverconfig.xml`, which — per the storage trade-off
above — is not reachable from this template's mount, and this Docker
wrapper documents no env var that sets it another way. None of the CRD's
three password mechanisms (`passwordSecretRef`, `passwordFile`,
operator-generated) has anywhere to deliver the value to the game. Rather
than invent an unconfirmed config, this template ships with RCON off. A
wrong config is worse than none.

No `lifecycle.stop` capability either (it requires RCON) — but this isn't
a gap: the image's own entrypoint (`user.sh`) traps `SIGINT`/`SIGTERM` and
runs LinuxGSM's own `sdtdserver stop`, which performs the game's graceful
save-and-shutdown itself. This game already saves cleanly on the pod's
normal SIGTERM.

## Mods

The generic Mods tab is not offered — `Mods/` lives under `serverfiles/`,
outside this template's mount, for the same reason `serverconfig.xml` is.
7 Days to Die mods are also folders (each with a `ModInfo.xml`), not loose
files, so the legacy single-file `mods.path`/`extensions` shape the
previous draft used (`.dll`/`.xml`/`.unity3d`) was wrong on top of being
unreachable.

Instead, this template exposes the image's own **first-install mod
installer** as config fields — independent of `storage.mountPath`, so it
still works: **Install Undead Legacy** / **Install Darkness Falls**
(overhaul mods, mutually exclusive), **Install Alloc's Fixes**, and
**Additional mod URLs** (comma-separated direct `.zip`/`.rar` links). Mods
install before the server is considered ready, and reinstall on every
restart since `serverfiles/` isn't persisted (same trade-off as above).

## Ports

| Name     | Port  | Protocol | Advertised |
| -------- | ----- | -------- | ---------- |
| game     | 26900 | TCP      | yes        |
| game-udp | 26900 | UDP      | yes        |
| game2    | 26901 | UDP      | yes        |
| game3    | 26902 | UDP      | yes        |
| telnet   | 8081  | TCP      | no         |

All four game ports must be reachable by clients for server discovery and
gameplay. `telnet` is declared but not advertised/used by Gameplane (see
Console & RCON above).

## Backups

A backup of the mount now correctly captures the world (saves +
generated-world data) — the previous mount captured nothing. It does
**not** capture `serverconfig.xml`, `Mods/`, or the server install;
restoring onto a fresh pod recovers the world and re-installs the server
around it (slow, automatic, not destructive).

## Known limitations

- No wizard-configurable server settings (name, max players, difficulty,
  PVP, day length, ...) — see Storage above. Set them by connecting to
  the running server's `serverfiles/serverconfig.xml` directly (Files tab
  won't help — that path isn't on the mounted volume) or accept the
  image's defaults.
- No RCON console, no player moderation/backup-quiesce capabilities.
- The previous draft's `consoleMode: pty` is **not** carried into this
  template — `consoleMode` is left unset, which now resolves to `"none"`
  automatically since `rcon.protocol` is `"none"`. Separately (and outside
  what this fix covers), PTY attach likely wouldn't have worked on this
  image anyway: LinuxGSM manages the game's own session, and the
  container's foreground process (per `install.sh`) ends up being a log
  `tail`, not the game's stdin. Flagged here rather than left silently
  assumed to work, since it wasn't independently verified.
