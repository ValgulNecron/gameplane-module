# `garrys-mod` module

Gameplane GameTemplate for Garry's Mod dedicated servers.

## Install

```sh
kubectl apply -f modules/garrys-mod/template.yaml
```

## Image

[`ceifa/garrysmod`](https://github.com/ceifa/garrysmod-docker) (`latest`/
`debian` tag). This image **bakes the game at build time** — a builder
stage runs `steamcmd +app_update 4020 validate` and the final image layer
already contains `garrysmod/addons`, `garrysmod/gamemodes`, `garrysmod/cfg`,
`garrysmod/lua`, and `garrysmod/maps`. The image declares exactly one
volume: `/home/gmod/server/garrysmod/data`. Everything else is intentionally
**not** a volume (per the image's own README) so it can be baked into a
derived image or bind-mounted by the operator running it.

This shapes everything below.

## Storage

`storage.mountPath` is `/home/gmod/server/garrysmod/data` — the one
directory this image is actually designed to persist. **Do not** change
this to a parent directory (e.g. `.../garrysmod` or `.../garrysmod/`
itself): an empty PVC mounted there shadows the baked `addons/`,
`gamemodes/`, `cfg/`, `lua/`, and `maps/` directories and srcds fails to
start. `data/` holds gamemode data and `sv.db` (a symlink target,
`garrysmod/sv.db` → `data/sv.db`) — that's what actually needs to survive a
pod restart for vanilla sandbox play.

## Console & RCON — intentionally disabled

This template ships with `rcon: { protocol: none }` and no `consoleMode`
(so the Console tab reports "no live console"). This isn't a placeholder —
it's the correct state given what's verified about this image:

- Source dedicated servers take `rcon_password` two ways: an
  auto-executed `garrysmod/cfg/server.cfg`, or a `+rcon_password <value>`
  launch token. `cfg/` is baked into the image outside `garrysmod/data`,
  so it's unreachable from `storage.mountPath` — `configFiles` paths can't
  contain `..` (enforced by the CRD), so there's no way to render into it.
- The only launch-arg hook this image exposes is the free-text `ARGS` env
  (appended unquoted to the srcds command line by the image's own
  `start.sh`). GameTemplate has no mechanism to compose a generated
  secret into a user-editable string field, and this image has no
  dedicated RCON-password env var — its documented env list is
  `PRODUCTION`/`NAME`/`MAXPLAYERS`/`GAMEMODE`/`MAP`/`PORT`/`GSLT`/`ARGS`/
  `AUTOUPDATE`/`PUID`/`PGID`. Nothing RCON-shaped.
- Separately (and moot given the above): the agent's RCON dial port is
  still hardcoded to 25575 (`agent/cmd/main.go`'s `--rcon-port` default);
  the operator does not pass `--rcon-port` from `GameTemplate.spec.rcon.
  port` anywhere in `buildAgentContainer`
  (`operator/internal/controller/gameserver_controller.go`). So even a
  correctly-authenticated RCON session couldn't dial the canonical 27015
  port today.

PTY console (attach to container stdin/stdout) was also considered —
srcds genuinely is the container's foreground process on this image, so
it would technically attach — but it's left off since there'd be no way
to authenticate an admin session for the moderation/backup capabilities
that depend on RCON anyway, and a console with no backing capabilities
would be misleading. `consoleMode` is left unset, which resolves to
`"none"` automatically once `rcon.protocol` is `"none"`.

## Mods — not supported by the panel

The generic Mods tab is not offered. The operator always mounts a mod
volume nested under `storage.mountPath` (`storage.mountPath/<path>`) —
never above it — but srcds reads addons from `garrysmod/addons`, a
**sibling** of `garrysmod/data`, not a child of it. No path under
`.../garrysmod/data/` is ever where srcds looks, and the CRD rejects `..`
in mod paths, so this is a structural mismatch, not a missing config.

**Workshop addon collections still work** without any of this: set
**Extra launch args** to `+host_workshop_collection <id> -authkey
<steam-web-api-key>` and the server downloads and mounts the collection
at boot — this is the image's own documented mechanism and doesn't touch
RCON or the addons directory.

For your own local addons/gamemodes, build a derived image (the image's
own recommended pattern):

```dockerfile
FROM ceifa/garrysmod:latest
COPY ./my-addons /home/gmod/server/garrysmod/addons
```

...and point `spec.image` at it.

## Ports

| Name     | Port  | Protocol | Advertised |
| -------- | ----- | -------- | ---------- |
| game     | 27015 | UDP      | yes        |
| game-tcp | 27015 | TCP      | no         |
| client   | 27005 | UDP      | no         |

Canonical Source dedicated-server ports (matches the image's own
`EXPOSE 27015` / `27015/udp` / `27005/udp`). `game-tcp` is the engine's
always-open TCP listener at the same port number (pings; would carry RCON
if it were configured) — used here only as the readiness/liveness probe
target, verified safe because the image's own `HEALTHCHECK` script relies
on the same TCP listener being bound regardless of RCON state.

## Known limitations

- No panel-managed addons/mods, no RCON console, no player
  moderation/backup-quiesce capabilities — see above for why, in detail.
- `AUTOUPDATE` (re-validate against Steam on every container start) is
  left at the image's own default (on) since this template doesn't
  expose it as a config field — toggling it needs a custom image env
  override outside the wizard.
- Bind-mount/PUID mismatches: the server runs as uid 1000 by default: if
  you change `PUID`/`PGID` outside this template, ensure the PVC's data
  is readable by that uid or srcds exits on startup instead of looping
  (the image's own entrypoint checks this explicitly).
