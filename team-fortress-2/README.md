# Team Fortress 2

Team Fortress 2 dedicated server backed by [cm2network/tf2](https://github.com/CM2Walki/TF2). Matches are session-based with persistent installation, Source RCON console, and MetaMod/SourceMod plugin capability.

## Install

```sh
kubectl apply -f modules/team-fortress-2/template.yaml
```

## Server Identity (GSLT)

To list your server in Valve's public server browser, obtain a Game Server Login Token (GSLT) for App ID `440` from [steamcommunity.com/dev/managegameservers](https://steamcommunity.com/dev/managegameservers) and supply it in `SRCDS_TOKEN`.

## Console & RCON

Remote management uses standard Source RCON on port 27015 TCP. The operator injects the password via `SRCDS_RCONPW`. Console actions include `say` (broadcast), `changelevel` (map change), and `mp_restartgame` (restart round).

The server stops cleanly by issuing the `quit` command before container shutdown.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 27015 | UDP | yes | Game traffic & Steam A2S query |
| `rcon` | 27015 | TCP | no | Source RCON administration |
| `sourcetv` | 27020 | UDP | yes | SourceTV spectator relay |

## Storage

Storage is mounted at `/home/steam/tf-dedicated` (15 GiB default). The mount path stores the downloaded server files and maps without shadowing the image entrypoint scripts in `/home/steam`.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment example.
