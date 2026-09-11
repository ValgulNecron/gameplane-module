# Gameplane Module Specification: Arma Reforger

## 1. Purpose & Scope

- **Game**: Arma Reforger
- **Module Slug**: `arma-reforger`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated multiplayer server for Bohemia Interactive's Arma Reforger, running on the Enfusion engine with interactive PTY console and Steam Workshop support.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/arma-reforger:latest@sha256:0000000000000000000000000000000000000000000000000000000000000000`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD Linux dedicated server (`ArmaReforgerServer`).
- **User & Execution Context**: UID 1000, GID 1000, working directory `/home/steam`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 2001 | UDP | Primary client gameplay traffic |
| `query` | 17777 | UDP | Steam A2S query discovery |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/steam/.local/share/ArmaReforgerServer`
- **Default Sizing**: `30Gi`
- **Persisted Content**:
  - Profile state and saved game sessions
  - Server configs (`ArmaReforgerServer.json`)
  - Downloaded Workshop addons (`addons/`)
- **Non-Shadowing Invariant**: The mount path isolates server state under `.local/share/ArmaReforgerServer`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none`
- **Console Mode**: `pty` (attaches to container stdin)
- **Authentication**: Admin password in server configuration.
- **Command Support**: In-engine CLI commands (`save`, `say`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Bohemia Interactive Workshop / addons.
- **Mod Directory Path**: `addons`

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "save"
  ```
- **Signal Handling**: Dedicated server initiates state flush on `SIGINT`/`SIGTERM`.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user (`steam`).
- **Environment**: `spec.env` contains `HOME=/home/steam`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` configured for volume ownership.

---

## 9. References & Upstream Documentation

- Bohemia Interactive Community Wiki - Arma Reforger Server Hosting: https://community.bistudio.com/wiki/Arma_Reforger:Server_Hosting
- Steam Dedicated Server AppID: 1874900
