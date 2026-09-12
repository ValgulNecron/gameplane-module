# BeamMP

BeamMP dedicated server for BeamNG.drive multiplayer soft-body physics simulation, powered by a Gameplane-owned container with diagnostic idle support (FR-013).

## Install

```sh
kubectl apply -f modules/beammp/template.yaml
```

## Server AuthKey

A BeamMP Server AuthKey is required to advertise your server on the BeamMP master list. Register a key at [beammp.com](https://beammp.com) and supply it in `BEAMMP_AUTH_KEY`.

If omitted, the server enters a non-crashing graceful diagnostic idle state (FR-013) that prints setup instructions in the pod log.

## Mods (Vehicles & Maps)

BeamNG vehicles, tracks, and map mods (`.zip` packages) can be dropped or uploaded into the `Resources/` folder managed through the **Mods** tab.

## Console (PTY)

BeamMP dedicated servers interact via standard input/output. The Gameplane Console tab connects via container PTY (`consoleMode: pty`).

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 30814 | UDP | yes | BeamMP client vehicle physics sync |
| `auth` | 30814 | TCP | yes | BeamMP server authentication and handshake |

## Storage

Persistent storage is mounted at `/server/Root` (5 GiB default), holding:
- `ServerConfig.toml`
- Downloaded and uploaded vehicle and map packages (`Resources/`)

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment manifest example.
