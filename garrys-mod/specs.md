# Gameplane Module Specification: Garry's Mod

## 1. Purpose & Scope

- **Game**: Garry's Mod
- **Module Slug**: `garrys-mod`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Physics sandbox dedicated server running on Valve's Source engine. Supports custom gamemodes (Sandbox, DarkRP, TTT) and Steam Workshop collection downloading via launch arguments.

---

## 2. Container Image & Architecture

- **Base Image**: `ceifa/garrysmod:latest@sha256:7c96a32cb2820c7410cb2305ca7ff1b173bfd7c041ea26a8d6715fbc52187c3e`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Pre-baked Source dedicated server (`srcds_run`) container image.
- **User & Execution Context**: Image user `gmod` (UID `1000`), working directory `/home/gmod/server`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `27015` | `UDP` | Primary client connection traffic |
| `game-tcp` | `27015` | `TCP` | Source engine TCP listener (probe target) |
| `client` | `27005` | `UDP` | Internal client ping/packet port |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/gmod/server/garrysmod/data`
- **Default Sizing**: `15Gi`
- **Persisted Content**:
  - Gamemode data, player persistence, and SQLite databases (`garrysmod/data/`)
  - Server logs and text state
- **Non-Shadowing Invariant**: Mount path isolates `/garrysmod/data` to prevent shadowing `/home/gmod/server` or `garrysmod/cfg` baked configs.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none` (deliberate, documented omission: `ceifa/garrysmod` bakes configuration with no password environment variable).
- **Console Mode**: `none`
- **Authentication**: N/A
- **Command Support**: N/A

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Steam Workshop Collections
- **Mod Directory Path**: Handled natively by Source engine via launch arguments (`+host_workshop_collection`).
- **Workshop Synchronization**: Automated at container launch by `srcds`.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**: `[]` (Empty; no RCON console reachable).
- **Signal Handling**: Container intercepts `SIGTERM` and halts `srcds_run` process cleanly.

---

## 8. Key Invariants & Security

- **User Matching**: Runs as user `1000` (`gmod`).
- **Storage Isolation**: Mounts only `/home/gmod/server/garrysmod/data` to avoid overwriting executable binaries.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://gmod.facepunch.com/
- Upstream Container Repository: https://github.com/ceifa/garrysmod
- Steam Dedicated Server AppID: `4020`
