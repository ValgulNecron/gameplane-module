# Gameplane Module Specification: Valheim (Dedicated)

## 1. Purpose & Scope

- **Game**: Valheim
- **Module Slug**: `valheim`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated server package for Iron Gate's Valheim, with BepInEx mod volume support, stable/public-test channel switching, and Thunderstore ecosystem integration.

---

## 2. Container Image & Architecture

- **Base Image**: `lloesche/valheim-server:latest@sha256:20fde516ce311e6084f82f295c9eb6934af57b357c657937a04f62bdf5946149`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD auto-install on container boot with supervisord process management.
- **User & Execution Context**: Image managed root/steam user with `/config` data directory.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 2456 | UDP | Main game traffic |
| `game2` | 2457 | UDP | Steam query traffic |
| `game3` | 2458 | UDP | Auxiliary / crossplay relay |
| `status` | 80 | TCP | Internal health and status metrics API |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/config`
- **Default Sizing**: `5Gi`
- **Persisted Content**:
  - World databases (`/config/worlds_local/`)
  - BepInEx plugins and configuration (`/config/bepinex/`)
  - Server identity files and admin lists (`adminlist.txt`)
- **Non-Shadowing Invariant**: The mount path isolates server state and mods under `/config`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none`
- **Console Mode**: `pty` (stdout streams server logs; status metrics queried via HTTP)
- **Authentication**: N/A
- **Command Support**: In-game administrative console via F5.

---

## 6. Modding & Workshop Integration

- **Modding Framework**: BepInEx plugins.
- **Mod Directory Path**: `bepinex/plugins`
- **Registry Integration**: Thunderstore community registry integration.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "save"
  ```
- **Signal Handling**: Container traps `SIGINT`/`SIGTERM` to initiate clean world persistence.

---

## 8. Key Invariants & Security

- **User Matching**: Default image execution.
- **Filesystem Permissions**: Persistent storage mounted at `/config`.

---

## 9. References & Upstream Documentation

- Valheim Dedicated Server Guide: https://valheim.fandom.com/wiki/Dedicated_servers
- Upstream Container Repository: https://github.com/lloesche/valheim-server-docker
- Steam Dedicated Server AppID: 896660
