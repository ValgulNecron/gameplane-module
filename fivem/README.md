# FiveM

FiveM dedicated server module for Grand Theft Auto V multiplayer, featuring single-pod txAdmin web management and embedded MariaDB database supervision (FR-012).

## Install

```sh
kubectl apply -f modules/fivem/template.yaml
```

## Authentication & License Key

A **CitizenFX server license key** is required for FiveM to start. Register a server key at [keymaster.fivem.net](https://keymaster.fivem.net) and provide it via the `CFX_LICENSE_KEY` secret.

If the license key is missing, the entrypoint enters a **graceful diagnostic idle** mode (FR-013) that prints instructions to the container log without crash-looping.

## Management & Remote Console (RCON)

Administration is driven through txAdmin's HTTP API (`rcon.protocol: rest`) listening on internal port 40120. Gameplane's agent connects directly to the REST API to execute console commands, broadcasts, and graceful shutdowns.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 30120 | UDP | yes | Primary client game traffic |
| `http` | 30120 | TCP | yes | FiveM client HTTP assets |
| `txadmin` | 40120 | TCP | no | Internal txAdmin web UI and REST API |

## Storage

Persistent storage is mounted at `/server-data`, retaining:
- Server configuration files (`server.cfg`)
- txAdmin configuration and user state (`txData/`)
- Embedded MariaDB database files (`mysql/`)
- Installed resources and assets (`resources/`)

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for an example deployment manifest.
