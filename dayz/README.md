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

## No console, no RCON

DayZ speaks proprietary **BattlEye RCon**, not Source RCON or telnet —
Gameplane's agent has no client for it, so `rcon.protocol: none`. The
game binary also has no interactive admin console of its own (admin is
BattlEye RCon, an external tool, or an in-game admin mod only), so no
`consoleMode` is set either — the Console tab shows "no live console."
With no reachable transport, there is no `capabilities` block at all: no
lifecycle stop sequence, no moderation, no quiesce. The server relies on
SIGTERM + DayZ's own autosave; whether that's fully safe under a bare
SIGTERM is not documented anywhere authoritative that was found —
consider a generous `stopGracePeriodSeconds` on the GameServer.

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
