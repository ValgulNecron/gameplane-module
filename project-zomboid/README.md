# `project-zomboid` module

Gameplane GameTemplate for Project Zomboid dedicated servers.

## Install

```sh
kubectl apply -f modules/project-zomboid/template.yaml
```

## Image

[`sknnr/zomboid-dedicated-server`](https://github.com/jsknnr/project-zomboid-server).

## Console & RCON

Project Zomboid's RCON is genuine Source-RCON-protocol — every actively
maintained RCON client library that supports PZ implements the plain
Source wire protocol with no special-casing. The **Console** tab, player
moderation (kick/ban), and the **Save world** action all ride this
connection (no `consoleMode` is set, so it defaults to `rcon`).

## Mods

Workshop mods are entirely config-driven: the game's own SteamCMD sync
downloads whatever is listed in **Workshop item IDs**, and **Mod IDs**
(the corresponding internal `mod.info` IDs, same order) activates them.
Both fields are required together — a Workshop item with no matching Mod
ID downloads but never loads. There is no panel-managed mods folder for
this game (no `capabilities.mods` block): Workshop content is entirely
game-managed via these two config fields, not files an admin drops in.

## Ports

| Name   | Port  | Protocol | Advertised |
| ------ | ----- | -------- | ---------- |
| game   | 16261 | UDP      | yes        |
| direct | 16262 | UDP      | yes        |
| rcon   | 27015 | TCP      | no         |

RCON is a separate port from the game port (unlike CS2/GMod), running on
PZ's canonical default, **27015**.

## Storage

The PVC mounts at `/home/steam`, covering both the image's install tree
(`zomboid/`) and its save/config tree (`zomboid_data/`) on one volume.
Default size is 15 GiB — heavy Workshop mod usage may need more.

## Backups

`AUTOSAVE_INTERVAL` controls the game's own periodic save; the **Save
world** action forces one immediately and is also what backup quiesce
runs before a snapshot. The image's own `BACKUPS_PERIOD`/`BACKUPS_COUNT`
env vars are not wired here — use the Gameplane Backup CRD as the
authoritative snapshot path instead.
