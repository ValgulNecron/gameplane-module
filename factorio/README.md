# Factorio (Headless)

Factorio headless server backed by the community-official
[factoriotools/factorio](https://github.com/factoriotools/factorio-docker)
image. The game ships **inside the image** (no steamcmd), so first boot only
generates the map. Saves, config, and mods all live under `/factorio` on the
server volume.

## Version picker

The image tag *is* the game version:

| Entry | Tag | Use when |
|---|---|---|
| Stable channel | `stable` | default; follows Factorio stable |
| Experimental channel | `latest` | newest experimental builds |
| 2.0.77 (pinned) | `stable-2.0.77` | freeze the game version entirely |

Each entry keeps its own mods volume, so channel switches never mix mod
sets. The pinned entry carries `gameVersion: "2.0"`, which filters the mod
portal browser to compatible mods; the moving channels show the full portal.

## Server settings

`server-settings.json` is rendered by the operator from the wizard fields
(name, description, game password, max players, public visibility, autosave
interval) on **every pod start** — edit them in the Settings tab and
restart. Anything not covered by the wizard (tags, admin list, upload
limits…) can be edited via the Files tab under `config/`; unknown keys fall
back to Factorio defaults.

> Public matchmaking (`PUBLIC`) requires your factorio.com `username` +
> `token` inside `server-settings.json`. The wizard deliberately doesn't
> collect those — add them via the Files tab if you want the server listed.

## Console — pty, no RCON (v1)

The image reads its RCON password from a self-generated file
(`/factorio/config/rconpw`) with no env override, so the panel's
secret-injected RCON password can never match — the agent could not
authenticate. The Console tab therefore attaches to **container stdin**
(pty), which accepts the same commands (`/save`, `/players`, `/ban` …).

Consequences, and why that's OK for v1:

- No Players tab / quiesce / one-click actions (all RCON-backed).
- Factorio **autosaves** (interval is a wizard field) and **saves on
  graceful shutdown**, so stops and backups still catch a consistent world.
- Operator follow-up noted: support for reading an RCON password from a
  file on the volume would unlock full RCON parity here.

## Mods

The Mods tab manages `.zip` mods in `/factorio/mods` (Factorio loads zips
directly — no extraction) and **browses the official mod portal** in-app,
filtered to the pinned entry's game version.

Portal downloads require *your own* factorio.com credentials — the panel
never stores them. Picking a file hands you to the from-URL form with the
portal URL prefilled; append `?username=YOU&token=TOKEN` (token from
[factorio.com/profile](https://factorio.com/profile)). GitHub-hosted mods
install directly, and local zips can be uploaded once the panel ships mod
upload. Set `UPDATE_MODS_ON_START` if you want mods synced to the game
version at boot.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a NodePort
deployment on the stable channel.
