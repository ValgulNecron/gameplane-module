# Counter-Strike 2

Counter-Strike 2 dedicated server backed by
[joedwards32/CS2](https://github.com/joedwards32/CS2) (the upstream project;
`cm2network/cs2` is a downstream mirror of the same image). CS2 has no
persistent world/save state — matches are stateless — so a container restart
never risks data loss the way a survival game's does.

## Install

```sh
kubectl apply -f modules/cs2/template.yaml
```

## Server identity (GSLT)

A **Game Server Login Token** is required for the server to appear on
Valve's matchmaking/server-browser network. Generate one at
[steamcommunity.com/dev/managegameservers](https://steamcommunity.com/dev/managegameservers)
(App ID `730`) and set it in the wizard's `SRCDS_TOKEN` field.

## Console & RCON

RCON is classic Source RCON on TCP 27015 (the game port, as a separate TCP
listener). The operator generates a password and injects it as `CS2_RCONPW`
— the Console tab, Broadcast action, and Stop button all use it (no
`consoleMode` override — it defaults to `rcon` since RCON is configured).

`quit` runs before the pod is scaled down, exiting immediately. CS2 keeps
no persistent world state, so there's nothing to save — using
`sv_shutdown` instead would make every stop wait for the current (and any
queued) match to finish, blocking the operator for the full
`stopGracePeriodSeconds` on every single stop for no benefit.

## Mods (Metamod / CounterStrikeSharp)

The Mods tab manages plugin binaries in `game/csgo/addons`:

- **Metamod** plugins are Linux `.so` binaries.
- **CounterStrikeSharp** plugins are `.dll` (.NET assemblies are `.dll` on
  every OS, including under CS#'s CoreCLR host on Linux). CS# itself nests
  one level deeper, at `game/csgo/addons/counterstrikesharp/plugins`, but
  install/upload targeting that subpath works the same way.

**Metamod/CS# must be bootstrapped once manually.** The Mods tab manages
*plugin* files, not the loader itself — Metamod's own `metamod.vdf` +
`metamod/` loader files aren't something the panel installs. Follow
[Metamod's install guide](https://cs2.poggu.me/metamod/installation/) via
the **Files** tab once, then use the Mods tab for individual plugins from
then on.

## Workshop maps

`CS2_HOST_WORKSHOP_COLLECTION` / `CS2_HOST_WORKSHOP_MAP` load a Steam
Workshop collection or single map on start. Workshop support on this image
is documented as experimental — there is no separate auth-key field; if a
map fails to download, check the Logs tab for the image's own diagnostics.

## GOTV / SourceTV

The image publishes a SourceTV relay port (`27020/udp`) alongside the game
port by default. It only does anything once GOTV is enabled via the
image's own `TV_ENABLE`/`TV_PORT` env vars (off by default) — this
template doesn't expose a wizard field for that yet, so set it through
`GameServer.spec.env` if you want spectators to be able to connect.

## Ports

| Name | Port  | Protocol | Advertised |
| ---- | ----- | -------- | ---------- |
| game | 27015 | UDP      | yes        |
| rcon | 27015 | TCP      | no         |
| gotv | 27020 | UDP      | yes        |

## Storage

Default PVC is 60 GiB at `/home/steam/cs2-dedicated` — the image's own
documented minimum for the install (base game + updates). Budget more if you
plan to keep several Workshop maps/collections cached.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a NodePort
deployment.
