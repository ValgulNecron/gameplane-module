# Left 4 Dead 2

Left 4 Dead 2 dedicated server backed by [left4devops/l4d2](https://github.com/left4devops/l4d2). Matches are session-based with persistent installation, Source RCON console, and MetaMod/SourceMod plugin capability.

## Install

```sh
kubectl apply -f modules/left-4-dead-2/template.yaml
```

## Console & RCON

Remote management uses standard Source RCON on port 27015 TCP. The operator injects the password via `RCON_PASSWORD`. Console actions include `say` (broadcast), `changelevel` (map change), and `kick` (player kick).

The server stops cleanly by issuing the `quit` command before container shutdown.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 27015 | UDP | yes | Game traffic |
| `query` | 27015 | UDP | yes | Steam A2S query |
| `rcon` | 27015 | TCP | no | Source RCON administration |

## Storage

Storage is mounted at `/home/steam/l4d2-dedicated` (15 GiB default). The mount path stores the downloaded server files and campaign addons without shadowing the image entrypoint scripts in `/home/steam`.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment example.
