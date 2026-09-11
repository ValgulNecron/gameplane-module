# The Isle

The Isle dedicated server package for Gameplane. Runs the dedicated server on Unreal Engine with persistent world saves, dinosaur population data, and Source RCON remote management.

## Install

```sh
kubectl apply -f modules/the-isle/template.yaml
```

## Console & RCON

Remote console access uses Source RCON on TCP port 8888. Set `RCON_PASSWORD` to authenticate. Administrative commands include `save` for triggering immediate world persistence, `announce` for global broadcasts, and `kick` for player moderation.

Graceful stop triggers the `save` command prior to container termination.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 7777 | UDP | yes | Client gameplay |
| `query` | 7778 | UDP | yes | Steam / A2S query |
| `rcon` | 8888 | TCP | no | Source RCON administration |

## Storage

Storage is mounted at `/serverdata/TheIsle/Saved` (25 GiB default). All world state, player profiles, and server configuration files persist across pod restarts.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment example.
