# ARK: Survival Evolved

ARK: Survival Evolved dedicated server package for Gameplane. Runs on Linux with persistent world state, Steam A2S server browser discovery, Source RCON console, and multi-server cluster transfer support.

## Install

```sh
kubectl apply -f modules/ark-survival-evolved/template.yaml
```

## Console & RCON

Remote management uses standard Source RCON on port 27020 TCP. The operator injects the password via `RCON_PASSWORD`. Console actions include `ServerChat` (broadcast), `SaveWorld` (world flush), and `KickPlayer` (moderation).

The server stops cleanly by issuing `SaveWorld` and `DoExit` prior to container termination.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 7777 | UDP | yes | Primary gameplay traffic |
| `query` | 27015 | UDP | yes | Steam A2S browser query |
| `rcon` | 27020 | TCP | no | Source RCON administration |

## Storage & Cluster Travel

Storage is mounted at `/serverdata/ShooterGame/Saved` (35 GiB default). All map saves, tribe data, player profiles, and cross-shard cluster transfers (`clusters/` subfolder) persist across container restarts.

To enable cluster travel between multiple ARK servers, supply the same `CLUSTER_ID` in each server's configuration and configure a shared volume or synchronize the cluster folder.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment example.
