# Gameplane Module Specification: Project Zomboid

## 1. Purpose & Scope

- **Game**: Project Zomboid
- **Module Slug**: `project-zomboid`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Hardcore isometric zombie survival multiplayer server. Supports persistent world state, survivor progression, building, and Steam Workshop mod synchronization.

---

## 2. Container Image & Architecture

- **Base Image**: `sknnr/zomboid-dedicated-server:latest@sha256:bcb7e2486214b93ee125051e888c87cfbe3aa2654897d944a6254272b7b0ab74`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Java/JVM dedicated server running under Linux with SteamCMD asset fetching.
- **User & Execution Context**: Rootless execution with UID `10000`, GID `10000`, working directory `/home/steam`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `16261` | `UDP` | Primary client connection port |
| `direct` | `16262` | `UDP` | Direct connect game port |
| `rcon` | `27015` | `TCP` | Source RCON administrative console |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/steam/Zomboid`
- **Default Sizing**: `15Gi`
- **Persisted Content**:
  - Saved worlds, maps, and player states (`Saves/`)
  - Server sandbox and configuration settings (`Server/`)
  - Whitelist, banlist, and admin accounts (`db/`)
- **Non-Shadowing Invariant**: Volume mounts cleanly to `/home/steam/Zomboid`, which houses the game's data files without shadowing the application binary or launcher scripts located in `/home/steam/zomboid-dedicated`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source`
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `spec.rcon.passwordEnv: RCON_PASSWORD`.
- **Command Support**: Standard Project Zomboid RCON commands (`servermsg`, `save`, `quit`, `players`, `kick`, `ban`, `gunshot`, `startrain`, `stoprain`, `startstorm`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Steam Workshop items configured via environment variables.
- **Mod Directory Path**: Native game-level synchronization using `MOD_IDS` and `WORKSHOP_IDS`.
- **Workshop Synchronization**: Handled natively by the dedicated server at launch via SteamCMD.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "save"
        - "quit"
  ```
- **Signal Handling**: Executes `save` and `quit` via Source RCON prior to container stopping, ensuring map chunks are committed to disk.

---

## 8. Key Invariants & Security

- **User Matching**: Image runs strictly as non-root user `10000`. `spec.security.runAsUser: 10000` matches image user.
- **Environment**: `spec.env` defines `HOME: /home/steam` to guarantee SteamCMD does not fail creating package directories.
- **Filesystem Permissions**: `spec.security.fsGroup: 10000` ensures proper ownership of mounted persistent storage.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://projectzomboid.com/
- Upstream Container Repository: https://github.com/jsknnr/project-zomboid-server
- Steam Dedicated Server AppID: `380870`
