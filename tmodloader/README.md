# tModLoader

tModLoader dedicated server for modded Terraria gameplay, packaged as a Gameplane module.

**Image:** [`passivelemon/terraria-docker`](https://github.com/PassiveLemon/terraria-docker) (`tmodloader-latest` tag)

## Install

```sh
kubectl apply -f modules/tmodloader/template.yaml
```

## Mod Management

tModLoader mods (`.tmod`) and modpacks are managed through the **Mods** tab. Mod files are stored under `/root/.local/share/Terraria/tModLoader/Mods`. Installs are allowed from GitHub release archives (max 512 MiB).

## Console (PTY)

Terraria engines do not provide an RCON TCP port. The **Console** tab attaches directly to the container's stdin/stdout (pty) using the kubelet pod-attach API. Stop sequence issues `exit` to trigger world flushing before shutdown.

## Ports

| Name | Port | Protocol | Advertised | Purpose |
| ---- | ---- | -------- | ---------- | ------- |
| `game` | 7777 | TCP | yes | Primary game traffic |

## Storage

Storage is mounted at `/root/.local/share/Terraria/tModLoader` (4 GiB default), holding:
- World files (`Worlds/`)
- Installed mods (`Mods/`)
- Mod configurations and loadouts

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a deployment manifest example.
