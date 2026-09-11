# Gameplane Module Specification: Farming Simulator 25

## 1. Purpose & Scope

- **Game**: Farming Simulator 25
- **Module Slug**: `farming-simulator-25`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Cooperative agricultural simulation dedicated server running under headless Wine. Features single-pod bundling of the game process with its official web administration portal.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/farming-simulator-25:latest@sha256:0000000000000000000000000000000000000000000000000000000000000000`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Headless Wine and dummy X11 (Xvfb) supervising the GIANTS dedicated server and web admin portal in a single-pod architecture (FR-012).
- **User & Execution Context**: UID `1000`, GID `1000`, working directory `/serverdata`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `10823` | `UDP` | Primary client game traffic |
| `web` | `8080` | `TCP` | Web administration and REST management portal |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/data/My Games/FarmingSimulator2025`
- **Default Sizing**: `20Gi`
- **Persisted Content**:
  - Farm progress, terrain modifications, and career saves (`savegame*`)
  - Server configuration files (`dedicated_server/`)
  - Downloaded mods and DLCs (`mods/`)
- **Non-Shadowing Invariant**: The mount path resides in `/data/My Games/FarmingSimulator2025` which is isolated from the container wineprefix and entrypoint scripts.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `rest`
- **Console Mode**: `none`
- **Authentication**: HTTP authentication against the web management portal using password from `spec.rcon.passwordEnv: ADMIN_PASSWORD`.
- **Command Support**: Save game and server status queries via web portal endpoints.

---

## 6. Modding & Workshop Integration

- **Modding Framework**: GIANTS Modhub and custom `.zip` vehicle/map packages
- **Mod Directory Path**: `mods`
- **Workshop Synchronization**: Web portal mod manager and manual upload.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "save"
  ```
- **Signal Handling**: Issues save to the web portal API and intercepts `SIGTERM` in `entrypoint.sh` to trigger clean server shutdown.

---

## 8. Key Invariants & Security

- **User Matching**: Container runs as UID `1000`, matching `spec.security.runAsUser: 1000`.
- **Environment**: `spec.env` defines `HOME: /home/gameplane`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` guarantees write permissions to the data mount.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://www.farming-simulator.com/
- Steam Dedicated Server AppID: `3016420`
