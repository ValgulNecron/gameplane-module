# `enshrouded` module

Gameplane GameTemplate for Enshrouded dedicated servers.

## Install

```sh
kubectl apply -f modules/enshrouded/template.yaml
```

## Console

Enshrouded has no remote admin console or RCON. Server administration is limited to editing configuration files and restarting the server. The **Console** tab shows container output for logging purposes.

## Ports

| Name  | Port  | Protocol | Advertised | Purpose |
| ----- | ----- | -------- | ---------- | ------- |
| game  | 15636 | UDP      | yes        | Game    |
| query | 15637 | UDP      | no         | Query   |

The query port is used for Steam server-browser listing only.

## Configuration

Player count is configured via the **Max Players** field in the New Server wizard (`SERVER_SLOT_COUNT`, range 1-16).

Enshrouded's role-based access control (Server Roles) is configured server-side via the image's environment variables (`SERVER_ROLE_*`), not through the Gameplane dashboard.

## Storage

Default PVC is 25 GiB at `/opt/enshrouded`. The server automatically saves every 10 minutes and on clean shutdown.

## Backups

A backup of the whole mount restores cleanly onto a fresh pod. Allow at least 90 seconds for a graceful shutdown during pod termination to ensure saves complete properly.

## Resources

Enshrouded is CPU- and memory-bound. Official minimum specs are quad-core 3.5GHz and 8GB RAM; full 16-slot servers benefit from 16GB+ RAM. The template defaults to 8GB request / 16GB limit with 2/4 CPU — adjust upward for heavily-modded or large-player servers.
