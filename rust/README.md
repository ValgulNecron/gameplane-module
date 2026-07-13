# Rust

Rust dedicated server backed by
[didstopia/rust-server](https://github.com/Didstopia/rust-server) (SteamCMD
install, data persists under `/steamcmd/rust`).

## Install

```sh
kubectl apply -f modules/rust/template.yaml
```

## Console — pty, no RCON

Rust's admin RCON is **WebSocket-only** (Facepunch's own `rcon.web`
tooling) — it does not speak the Source RCON wire protocol the agent
implements, and there is no raw-TCP fallback. `rcon.protocol` is therefore
`none`; the **Console** tab instead attaches to the container's stdin/stdout
(pty), the same transport every community Docker/tmux wrapper uses to drive
RustDedicated's interactive console.

Consequences:

- No Players tab, moderation, quiesce, or one-click actions — all of those
  are RCON-backed everywhere in Gameplane, and Rust has no reachable RCON.
- The template declares `capabilities.lifecycle.stop: ["server.save",
  "quit"]` (the documented clean-shutdown sequence) for when Gameplane's
  operator gains a PTY-stdin stop path — until then it's a documented no-op,
  and the server relies on its own autosave interval plus a generous
  `terminationGracePeriodSeconds` on SIGTERM.
- Port 28016 (WebRCON) is declared but not advertised — Gameplane doesn't
  use it. If you want a third-party WebRCON client (e.g. rustadmin), expose
  it yourself via `networking.portOverrides`.

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
