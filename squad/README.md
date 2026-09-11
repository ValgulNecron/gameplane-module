# Squad

Squad dedicated server package for Gameplane. Runs Unreal Engine 4 dedicated server with large-scale 50v50 combined arms matches, persistent server configs and rotation logs, and Source-family RCON console administration.

## Install

```sh
kubectl apply -f modules/squad/template.yaml
```

## Console & RCON

Remote management uses standard Source RCON on port 21114 TCP. The operator injects the password via `RCON_PASSWORD`. Console actions include `AdminBroadcast` (announcement), `AdminChangeLayer` (map change), and `AdminKick` (moderation).

Gameplay is match-based, and server shutdown does not require a pre-shutdown save command.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 7787 | UDP | yes | Client gameplay |
| `query` | 27165 | UDP | yes | Steam A2S query discovery |
| `rcon` | 21114 | TCP | no | Source RCON administration |

## Storage

Persistent storage is mounted at `/serverdata/Squad/Saved` (40 GiB default). Server settings, admin lists, and map rotation history persist across container restarts.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment example.
