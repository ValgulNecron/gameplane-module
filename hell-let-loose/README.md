# Hell Let Loose

Hell Let Loose dedicated server package for Gameplane. Runs Unreal Engine dedicated server with match-based gameplay, persistent configuration and logs, Source RCON console on port 22222, and preset community version support.

## Install

```sh
kubectl apply -f modules/hell-let-loose/template.yaml
```

## Console & RCON

Remote management uses standard Source RCON on port 22222 TCP. The operator injects the password via `RCON_PASSWORD`. Console actions include `say` (broadcast), `map` (map change), and `kick` (moderation).

Gameplay is match-based, and server termination does not require a pre-shutdown save command.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 7787 | UDP | yes | Primary gameplay traffic |
| `query` | 27165 | UDP | yes | Steam A2S query discovery |
| `rcon` | 22222 | TCP | no | Source RCON administration |

## Storage

Persistent storage is mounted at `/serverdata/HLL/Saved` (35 GiB default). Server settings, admin lists, and match logs persist across container restarts.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment example.
