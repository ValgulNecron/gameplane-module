# `dont-starve-together` module

Gameplane GameTemplate for Don't Starve Together dedicated servers.

## Install

```sh
kubectl apply -f modules/dont-starve-together/template.yaml
```

## Cluster Token

Don't Starve Together requires a **Cluster Token** for public/online gameplay. Obtain one free from your Klei Entertainment account:

1. Visit <https://accounts.klei.com>
2. Go to **Don't Starve Together** → **Servers** → **Create New Cluster**
3. Copy the cluster token
4. Paste it into the **Cluster Token** field in the New Server wizard

LAN-only servers can skip this step.

## Console

No RCON. The **Console** tab attaches to the container's stdin/stdout (pty) for Lua console commands.

## Mods

Mods are managed through the game's Steam Workshop integration. Workshop mod IDs are configured server-side via the image's settings, not through the Gameplane Mods tab. For Workshop support, configure `dedicated_server_mods_setup.lua` on the server volume.

## Ports

| Name   | Port  | Protocol | Advertised | Purpose           |
| ------ | ----- | -------- | ---------- | ----------------- |
| game   | 10999 | UDP      | yes        | Master shard      |
| caves  | 11000 | UDP      | yes        | Caves shard       |
| steam1 | 12346 | UDP      | no         | Steam networking  |
| steam2 | 12347 | UDP      | no         | Steam networking  |

All four ports are required for online servers; LAN-only setups use the game port (10999) only.

## Storage

Default PVC is 5 GiB at `/data`; cluster save data and configuration live there.

## Backups

A backup of the whole mount restores cleanly onto a fresh pod.
