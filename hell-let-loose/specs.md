# Gameplane Module Specification: Hell Let Loose

## 1. Purpose & Scope

- **Game**: Hell Let Loose
- **Module Slug**: `hell-let-loose`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated multiplayer server for Black Matter / Team17's Hell Let Loose, featuring large-scale 100-player WWII matches, Source RCON console administration, and optional Vietnam community preset.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/hell-let-loose:latest@sha256:0000000000000000000000000000000000000000000000000000000000000000`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD Linux dedicated server running Unreal Engine.
- **User & Execution Context**: UID 1000, GID 1000, working directory `/serverdata`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 7787 | UDP | Primary client gameplay traffic |
| `query` | 27165 | UDP | Steam A2S query discovery |
| `rcon` | 22222 | TCP | Remote administrative console (Source RCON) |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/serverdata/HLL/Saved`
- **Default Sizing**: `35Gi`
- **Persisted Content**:
  - Server configuration files (`Game.ini`, `Engine.ini`)
  - Admin lists and ban files
  - Match history and rotation logs
- **Non-Shadowing Invariant**: The mount path isolates the `Saved/` directory without shadowing the server binaries in `/serverdata`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source`
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `RCON_PASSWORD`.
- **Command Support**: Standard HLL RCON commands (`say`, `map`, `kick`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Unreal Engine / community mod presets.
- **Mod Directory Path**: Handled via version catalog presets.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  - Stateless match-based architecture; no world save required prior to shutdown.
- **Signal Handling**: Server cleanly handles `SIGINT`/`SIGTERM`.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user.
- **Environment**: `spec.env` contains `HOME=/serverdata`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` configured for volume permissions.

---

## 9. References & Upstream Documentation

- Hell Let Loose Server Administration: https://www.hellletloose.com/
- Steam Dedicated Server AppID: 686810
