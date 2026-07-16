# `dayz` module

Gameplane GameTemplate for DayZ dedicated servers.

## Install

```sh
kubectl apply -f modules/dayz/template.yaml
```

## Image

[`GodBleak/ServerZ`](https://github.com/GodBleak/ServerZ), pulled from
the project's own OCI registry:
`registry.godbleak.dev/godbleak/serverz:latest`. This replaces the
previous draft's `jammsen/dayz-dedicated-server`, which does not exist on
any registry.

**Not Docker Hub or GHCR.** The image is hosted on the project's
self-hosted GitLab container registry — verified reachable and
anonymously pullable (`docker pull` needs no login), but it is a single
maintainer's own infrastructure rather than a major registry. If that's
a concern for your deployment, mirror the image into your own registry
before installing.

## Console and admin

DayZ speaks proprietary **BattlEye RCon** — not Source RCON or telnet.
Gameplane's agent implements it (`rcon.protocol: battleye`, UDP 2305), so
the Console tab and the players list both work. ServerZ only writes a
`beserver_x64.cfg` when one of `BE_IP`/`BE_PORT`/`BE_PASSWORD` is set, so
this template sets all three: the operator injects the generated password
into `BE_PASSWORD`, and `BE_IP` pins the listener to loopback — the agent
sidecar shares the pod's network namespace and reaches it there, while an
RCon port that isn't on a public interface can't be brute-forced.

**No kick/ban buttons, and no quick actions.** BattlEye targets players by
*number* rather than name, so wiring moderation to the name the list
returns would risk hitting the wrong player. Its command set is also too
restricted to verify a broadcast for DayZ specifically, so no quick actions
are declared rather than shipping buttons that may error.

**No lifecycle stop sequence.** DayZ persists continuously rather than on a
save command, so a SIGTERM isn't the data-loss risk it is for Minecraft or
Valheim; a stop sequence that doesn't reliably work across builds would be
a lie. Consider a generous `stopGracePeriodSeconds` on the GameServer.

## Mods

**Workshop mod IDs** is a plain config field (comma-separated Steam
Workshop item IDs) — DayZ mods are `-mod=` launch-parameter driven, not a
panel-managed folder, so there is no `capabilities.mods` block.

**Mods require a one-time interactive Steam login.** The base dedicated
server installs anonymously (no Steam account needed) — but Workshop
downloads need one. ServerZ's recommended flow is a QR code shown in the
container logs (scan with the Steam mobile app); this can't be automated
through the Gameplane dashboard today. To use mods:

1. Set **Workshop mod IDs**, start the server, then `kubectl logs` the
   game pod and scan the QR code within its timeout.
2. This template does **not** persist `/root/.steam` (see Storage below),
   so a rescheduled/restarted pod loses that login and needs it redone.

Running with no mods needs none of this.

## Ports

| Name  | Port  | Protocol | Advertised |
| ----- | ----- | -------- | ---------- |
| game  | 2302  | UDP      | yes        |
| query | 27015 | UDP      | no         |

## Storage

The image documents four separate paths (`/data`, `/overrides`,
`/install`, `/root/.steam`) with no common parent besides `/` — only
`/data` (world/profile state) is mounted here. `/install` is left
ephemeral, so **every pod (re)start re-downloads the full ~10GB+ server
via SteamCMD** — the same tradeoff the shipped `valheim` module already
makes with its own SteamCMD-on-boot image. Default size is 40 GiB.

## No readiness/liveness probes

Every port this image exposes is UDP, and it has no HTTP endpoint —
there is no TCP or HTTP surface to probe, so none is declared. Kubernetes
falls back to treating the pod as ready once the container is running.
