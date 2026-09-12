# Arma Reforger

Arma Reforger dedicated server package for Gameplane. Runs on Bohemia Interactive's Enfusion engine with interactive PTY stdin console, persistent profile and saves, and Steam Workshop modding support.

## Install

```sh
kubectl apply -f modules/arma-reforger/template.yaml
```

## Console

No RCON protocol. The **Console** tab attaches directly to container stdin/stdout (pty) for administrative commands. Server stop issues `save` prior to pod termination.

## SteamCMD Login

Most dedicated servers allow anonymous SteamCMD download. If an authenticated Steam login is required to pull specific game builds or workshop dependencies, provide credentials in `STEAM_USER` and `STEAM_PASSWORD`.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 2001 | UDP | yes | Client gameplay |
| `query` | 17777 | UDP | yes | Steam / A2S query |

## Storage

Persistent storage is mounted at `/home/steam/.local/share/ArmaReforgerServer` (30 GiB default). All world state, player profiles, and downloaded Workshop mods persist across container restarts.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment example.
