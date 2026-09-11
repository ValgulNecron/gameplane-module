# Rust

Rust dedicated server backed by
[didstopia/rust-server](https://github.com/Didstopia/rust-server) (SteamCMD
install, data persists under `/steamcmd/rust`).

## Install

```sh
kubectl apply -f modules/rust/template.yaml
```

## Console & Remote Management (WebRCON)

Rust's administrative interface uses **WebSocket-over-TCP** (Facepunch's `rcon.web` / WebRCON). The Gameplane agent implements this natively (`rcon.protocol: websocket`), connecting in-pod to port 28016 with password authentication supplied via `RUST_RCON_PASSWORD`.

- Console tab connects directly over WebRCON.
- Live player list with regex extraction of display names.
- Moderation (kick, ban) and server actions (broadcast, save-world, announce-restart).
- Graceful stop sequence executes `server.save` followed by `quit` over RCON before pod termination.

## Version picker (Oxide / Carbon)

| Entry | Loader | Volume |
|---|---|---|
| Vanilla | *(none)* | — no Mods tab |
| Oxide | `oxide` | `oxide/plugins` (`.cs`) |
| Carbon | `carbon` | `carbon/plugins` (`.cs`) |

Switching selects `RUST_OXIDE_ENABLED` for the image's built-in Oxide
support. **Carbon has no equivalent image flag** — didstopia/rust-server
only documents Oxide. Carbon's own loader must be installed manually (via
the Files tab) before plugins dropped in the Carbon volume take effect;
Carbon's compiled Harmony mods live in a separate `HarmonyMods/`-style path
this module doesn't manage — only Carbon's own `.cs` plugins are.

Each version+loader combination keeps its own PVC, so switching never mixes
Oxide and Carbon plugin sets.

## Ports

| Name | Port  | Protocol | Advertised |
| ---- | ----- | -------- | ---------- |
| game | 28015 | UDP      | yes        |
| rcon | 28016 | TCP      | no (WebRCON — unused by Gameplane) |

## Sample

See [`samples/gameserver.yaml`](samples/gameserver.yaml) for a NodePort
deployment.
