# V Rising

V Rising dedicated server backed by
[trueosiris/vrising](https://github.com/TrueOsiris/docker-vrising)
(Ubuntu 22.04 + Wine).

## Install

```sh
kubectl apply -f modules/v-rising/template.yaml
```

## Console & RCON

V Rising's dedicated server speaks genuine **Source RCON** (confirmed
against Stunlock's own RCON instructions and third-party Source-RCON
clients such as `gorcon/rcon-cli`), enabled in `ServerHostSettings.json`.
The image has no dedicated env flag for this, but does support a generic
`HOST_SETTINGS_<Key>__<NestedKey>=value` passthrough that patches the JSON
config at boot (double underscore = nested key) — the template uses it to
turn RCON on (`HOST_SETTINGS_Rcon__Enabled=true`) and to receive the
operator-generated password (`HOST_SETTINGS_Rcon__Password`).

The Console tab, **Broadcast** action (`announce`), and Stop button all use
RCON. Stop runs `shutdown 0 <message>` (Stunlock's documented RCON
shutdown command) before the pod scales down, so a SIGTERM never interrupts
an in-progress autosave.

## Storage layout

The image documents two persistent paths — `/mnt/vrising/server` (game
install) and `/mnt/vrising/persistentdata` (world/settings) — both meant to
survive restarts (the project's own `docker-compose.yml` example bind-mounts
both). Gameplane provisions one PVC per template, so `storage.mountPath` is
set to their common parent, `/mnt/vrising`; both subdirectories land on it
and a Backup snapshot covers everything (install, saves, and installed
mods) in one shot.

## Ports

| Name  | Port | Protocol | Advertised |
| ----- | ---- | -------- | ---------- |
| game  | 9876 | UDP      | yes        |
| query | 9877 | UDP      | yes        |
| rcon  | 25575| TCP      | no         |

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a NodePort
deployment.
