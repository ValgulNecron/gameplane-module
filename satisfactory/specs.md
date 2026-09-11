# Gameplane Module Specification: Satisfactory (Dedicated)

## 1. Purpose & Scope

- **Game**: Satisfactory
- **Module Slug**: `satisfactory`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated multiplayer server for Coffee Stain Studios' Satisfactory, featuring automated SteamCMD installation, branch selection (stable/experimental), and HTTPS administrative API control.

---

## 2. Container Image & Architecture

- **Base Image**: `wolveix/satisfactory-server:latest@sha256:e103700ae6ae4c50f19dac80eadb2a805c5b885e179ae2a40850e967bf189efd`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD auto-install on container boot with gosu privilege drop.
- **User & Execution Context**: Image entrypoint drops to PUID 1000 / PGID 1000, working directory `/config`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 7777 | UDP | Primary client gameplay traffic |
| `game-tcp` | 7777 | TCP | HTTPS API and game connection signaling |
| `messaging` | 8888 | TCP | Game socket signaling and messaging |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/config`
- **Default Sizing**: `25Gi`
- **Persisted Content**:
  - Downloaded server binaries and SteamCMD caches
  - Saved factories and worlds (`/config/saved/server-saves`)
  - Server configuration and claimed credentials
- **Non-Shadowing Invariant**: The container image installs binaries into `/config` during startup.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `satisfactory` (HTTPS API on port 7777)
- **Console Mode**: `rcon`
- **Authentication**: Password stored in `/config/gameplane/rcon-admin-password` (relative path `gameplane/rcon-admin-password`).
- **Command Support**: HTTPS API `RunCommand` executing `server.SaveGame`.

---

## 6. Modding & Workshop Integration

- **Modding Framework**: None built-in (mod manager out-of-scope for vanilla dedicated server).

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "SaveGame"
  ```
- **Signal Handling**: Container entrypoint intercepts `SIGTERM` and initiates clean save and exit.

---

## 8. Key Invariants & Security

- **User Matching**: Starts as root to chown `/config`, then drops privileges to UID/GID 1000 via gosu.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` ensures correct volume ownership across Kubernetes drivers.

---

## 9. References & Upstream Documentation

- Satisfactory Dedicated Server Documentation: https://satisfactory.wiki.gg/wiki/Dedicated_servers
- Upstream Container Repository: https://github.com/wolveix/satisfactory-server
- Steam Dedicated Server AppID: 1690800
