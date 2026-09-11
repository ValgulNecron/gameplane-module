# Gameplane Module Specification: Squad

## 1. Purpose & Scope

- **Game**: Squad
- **Module Slug**: `squad`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated multiplayer server for Offworld Industries' Squad, featuring 100-player tactical military matches, Unreal Engine 4 server runtime, and Source-family RCON console administration.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/squad:latest@sha256:0000000000000000000000000000000000000000000000000000000000000000`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD Linux dedicated server (`SquadServer.sh`).
- **User & Execution Context**: UID 1000, GID 1000, working directory `/serverdata`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 7787 | UDP | Primary client gameplay traffic |
| `query` | 27165 | UDP | Steam A2S query discovery |
| `rcon` | 21114 | TCP | Remote administrative console (Source RCON) |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/serverdata/Squad/Saved`
- **Default Sizing**: `40Gi`
- **Persisted Content**:
  - Server configuration files (`Server.cfg`, `Admins.cfg`, `LayerRotation.cfg`)
  - Server bans and player licenses
  - Match history and performance logs
- **Non-Shadowing Invariant**: The mount path isolates the `Saved/` directory without shadowing the server binaries in `/serverdata`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source`
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `RCON_PASSWORD`.
- **Command Support**: Standard Squad RCON commands (`AdminBroadcast`, `AdminChangeLayer`, `AdminKick`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Steam Workshop (`Plugins/Mods`).
- **Mod Directory Path**: `Plugins/Mods`

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  - Stateless match-based architecture; no world save required prior to shutdown.
- **Signal Handling**: Server cleanly handles `SIGINT`/`SIGTERM`.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user.
- **Environment**: `spec.env` contains `HOME=/serverdata`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` configured for volume ownership.

---

## 9. References & Upstream Documentation

- Squad Dedicated Server Administration Guide: https://squad.fandom.com/wiki/Server_Administration
- Steam Dedicated Server AppID: 403240
