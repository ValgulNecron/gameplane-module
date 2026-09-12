# Gameplane Module Specification: ARK: Survival Evolved

## 1. Purpose & Scope

- **Game**: ARK: Survival Evolved
- **Module Slug**: `ark-survival-evolved`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated multiplayer server for Studio Wildcard's ARK: Survival Evolved. Manages persistent world saves, multi-shard cluster transfers, and Source RCON administration.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/ark-survival-evolved:latest@sha256:0000000000000000000000000000000000000000000000000000000000000000`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD Linux dedicated server (`ShooterGameServer`).
- **User & Execution Context**: UID 1000, GID 1000, working directory `/serverdata`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 7777 | UDP | Primary gameplay traffic |
| `query` | 27015 | UDP | Steam A2S browser discovery |
| `rcon` | 27020 | TCP | Remote administrative console (Source RCON) |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/serverdata/ShooterGame/Saved`
- **Default Sizing**: `35Gi`
- **Persisted Content**:
  - Saved worlds, tribe data, and dinosaur entities (`SavedArks/`)
  - Server configuration files (`Config/LinuxServer/GameUserSettings.ini`)
  - Cross-server cluster transfers (`clusters/`)
- **Non-Shadowing Invariant**: The mount path isolates the `Saved/` directory without shadowing the server binaries in `/serverdata`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source`
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `RCON_PASSWORD`.
- **Command Support**: In-game moderation (`KickPlayer`, `BanPlayer`), world saving (`SaveWorld`), broadcasts (`ServerChat`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Steam Workshop (`-automanagedmods`).
- **Mod Directory Path**: Managed within image install.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "SaveWorld"
        - "DoExit"
  ```
- **Signal Handling**: Server cleanly saves before terminating on `SIGINT`/`SIGTERM`.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user.
- **Environment**: `spec.env` contains `HOME=/serverdata`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` ensures volume read/write permissions.

---

## 9. References & Upstream Documentation

- ARK: Survival Evolved Dedicated Server: https://ark.wiki.gg/wiki/Dedicated_server_setup
- Steam Dedicated Server AppID: 376030
