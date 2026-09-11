# Mount & Blade II: Bannerlord

Mount & Blade II: Bannerlord dedicated multiplayer server for hosting custom skirmish, battle, and siege sessions.

## Install

```sh
kubectl apply -f modules/mount-and-blade-2-bannerlord/template.yaml
```

## Server Authentication Token

TaleWorlds requires a dedicated server token to list your server on the official master list. Generate a token inside the game client by opening the console and running `customserver.gettoken`, then configure `SERVER_TOKEN`.

## Console (PTY)

Bannerlord dedicated servers run an interactive CLI on standard input. The Gameplane dashboard attaches directly via container PTY (`consoleMode: pty`). Matches are session-based with no persistent campaign state.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 7210 | UDP | yes | Primary client game traffic |
| `query` | 7211 | UDP | yes | Steam A2S query & master browser |

## Storage

Storage is mounted at `/serverdata` (20 GiB default) to hold the server binaries, configuration templates, and custom module XMLs.

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for an example deployment manifest.
