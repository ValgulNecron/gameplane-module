# Euro Truck Simulator 2

Euro Truck Simulator 2 dedicated convoy server backed by a Gameplane-owned container with diagnostic idle support (FR-013).

## Install

```sh
kubectl apply -f modules/euro-truck-simulator-2/template.yaml
```

## Server Logon Token

An authenticated Steam server logon token is required for the dedicated server to register with Steam's session coordinator. Obtain a token for App ID `1948400` from [steamcommunity.com/dev/managegameservers](https://steamcommunity.com/dev/managegameservers) and supply it via `SERVER_LOGON_TOKEN`.

If the token is omitted or empty, the server enters a graceful idle state (FR-013) that displays diagnostic setup instructions in the pod log instead of crash-looping.

## Console (PTY)

ETS2 dedicated servers do not expose an RCON TCP port. Remote console interaction runs through container stdin/stdout (`consoleMode: pty`). Graceful stop issues `exit` to the console.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 27015 | UDP | yes | Convoy multiplayer traffic |
| `query` | 27016 | UDP | yes | Steam A2S query & discovery |

## Storage

Storage is mounted at `/home/steam/.local/share/Euro Truck Simulator 2` (10 GiB default), retaining:
- Convoy configuration (`server_config.sii`)
- Server logs and player records
- Custom packages and mod manifests

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for an example deployment manifest.
