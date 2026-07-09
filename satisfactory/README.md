# Satisfactory (Dedicated)

Satisfactory dedicated server backed by the community
[wolveix/satisfactory-server](https://github.com/wolveix/satisfactory-server)
image. The game server is installed and updated by **steamcmd at container
start**, so it always tracks Steam.

> **First boot is slow.** steamcmd downloads several GB before the server
> listens. There is no readiness probe (the game speaks UDP and exposes no
> HTTP/TCP health endpoint usable as a gate), so the pod reports Ready
> quickly while the download runs — watch progress in the dashboard's Logs
> tab (source "pod") and give it a few minutes on the first start.

## Version picker

The wizard's version picker selects the **Steam branch**. Both entries run
the same image; the choice sets `STEAMBETA`:

| Entry | `STEAMBETA` | Use when |
|---|---|---|
| Stable | `false` | default; the public release |
| Experimental | `true` | the experimental build |

## Console & admin

Satisfactory has **no RCON and no stdin console**, so this module declares
`rcon.protocol: none` and `consoleMode: none` — there is no Console tab, and
no player-moderation, quiesce, or graceful-stop-command capabilities. Manage
the server in-game (the first client to connect claims it and sets the admin
password) or through its config; the server saves and shuts down cleanly on
SIGTERM when the pod stops.

## Configuration

The New Server wizard surfaces the image's env vars:

| Field | Env | Default | Purpose |
|---|---|---|---|
| Max players | `MAXPLAYERS` | `4` | player limit |
| Max tick rate | `MAXTICKRATE` | `30` | simulation tick rate (Hz) |
| Autosave slots | `AUTOSAVENUM` | `5` | rotating autosave files kept |
| Client timeout | `TIMEOUT` | `30` | seconds before dropping an idle client |

The server runs as a fixed non-root uid/gid (`PUID`/`PGID` = 1000); gosu
drops from root after fixing ownership on the data volume.

## Ports

Satisfactory 1.0 uses a single game port (7777, both UDP and TCP) plus a TCP
messaging port (8888). All three are advertised, since clients need them.

## Storage & backups

The whole install lives on the `/config` volume (`gamefiles`, `saved`,
`logs`, `backups`), so game files and world saves persist together. Backups
snapshot `/config` directly; there is no quiesce, so backup freshness rides
the server's autosave.
