# Gameplane Module Specification: Rust

## 1. Purpose & Scope

- **Game**: Rust
- **Module Slug**: `rust`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Harsh multiplayer survival game dedicated server developed by Facepunch Studios. Backed by `didstopia/rust-server`, supporting persistent procedural worlds, WebRCON management, and Oxide/uMod plugin extension.

---

## 2. Container Image & Architecture

- **Base Image**: `didstopia/rust-server:latest@sha256:a16589d9182245faee4353cd99e59965e6a9bec17d3d757bb427c48a17546a2b`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD Linux dedicated server runner wrapped with Oxide bootstrap options.
- **User & Execution Context**: Starts as root and executes via `didstopia/rust-server` runtime scripts. Working directory `/steamcmd/rust`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `28015` | `UDP` | Primary client game traffic & server query |
| `rcon` | `28016` | `TCP` | WebRCON administrative websocket interface |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/steamcmd/rust`
- **Default Sizing**: `10Gi`
- **Persisted Content**:
  - Procedural map files and world save data (`server/my_server_identity/`)
  - Server identity files and player blueprints
  - Oxide configuration and plugins (`oxide/`)
- **Non-Shadowing Invariant**: Mount path stores game data and downloaded server content; does not shadow entrypoint launcher scripts.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `websocket` (Facepunch WebRCON over TCP)
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `spec.rcon.passwordEnv: RUST_RCON_PASSWORD`.
- **Command Support**: Standard Facepunch console commands (`playerlist`, `say`, `server.save`, `env.time`, `restart`, `kick`, `ban`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Oxide / uMod plugin loader (C# `.cs` scripts)
- **Mod Directory Path**: `oxide/plugins`
- **Workshop Synchronization**: uMod registry integration with in-app plugin installation.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "server.save"
        - "quit"
  ```
- **Signal Handling**: Executes world save and quit command sequence over WebRCON to prevent rollback before pod termination.

---

## 8. Key Invariants & Security

- **User Matching**: Runtime permissions handled by `didstopia/rust-server` entrypoint.
- **RCON Protocol**: `websocket` on port 28016 connects internally inside the pod network; not publicly advertised.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://rust.facepunch.com/
- Upstream Container Repository: https://github.com/Didstopia/rust-server
- Steam Dedicated Server AppID: `258550`
