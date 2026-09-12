# Farming Simulator 25

Farming Simulator 25 dedicated server running via a headless Wine runtime environment with an integrated web management portal (FR-012).

## Install

```sh
kubectl apply -f modules/farming-simulator-25/template.yaml
```

## Web Management Portal & REST API

Farming Simulator dedicated servers do not expose an interactive stdin console or traditional TCP/UDP RCON socket. Instead, the dedicated server features a built-in web management portal listening on TCP port 8080.

Gameplane's agent communicates directly with the portal's HTTP endpoints (`rcon.protocol: rest`) to query server status and trigger game saves prior to shutdown.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 10823 | UDP | yes | Primary client game traffic |
| `web` | 8080 | TCP | yes | Dedicated server web administration portal |

## Storage

Storage is mounted at `/data/My Games/FarmingSimulator2025` (20 GiB default), persisting:
- Savegames and farm progress (`savegame1/`, etc.)
- Server configuration files (`dedicated_server/`)
- Mod downloads and activate state (`mods/`)

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment manifest example.
