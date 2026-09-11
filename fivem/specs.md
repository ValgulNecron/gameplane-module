# Gameplane Module Specification: FiveM

## 1. Purpose & Scope

- **Game**: FiveM (Grand Theft Auto V Multiplayer)
- **Module Slug**: `fivem`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated server framework for GTA V roleplay and custom game modes. Bundles txAdmin web management and embedded MariaDB database in a single pod container architecture.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/fivem:latest`
- **Architecture**: `linux/amd64`
- **Runtime Model**: CitizenFX server supervised alongside embedded MariaDB and txAdmin in a single-pod architecture (FR-012).
- **User & Execution Context**: UID `1000`, GID `1000`, working directory `/server-data`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `30120` | `UDP` | Primary client game traffic |
| `http` | `30120` | `TCP` | Asset downloading and client HTTP communication |
| `txadmin` | `40120` | `TCP` | Internal txAdmin web UI and REST management API |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/server-data`
- **Default Sizing**: `20Gi`
- **Persisted Content**:
  - txAdmin profiles and configuration (`txData/`)
  - Server configuration files (`server.cfg`)
  - Embedded MariaDB relational data (`mysql/`)
  - Custom resources, scripts, and assets (`resources/`)
- **Non-Shadowing Invariant**: The mount path `/server-data` hosts the writable server assets and state without overriding `/opt/cfx-server` or system binaries.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `rest`
- **Console Mode**: `rcon`
- **Authentication**: Token supplied via `spec.rcon.passwordEnv: TXADMIN_TOKEN`.
- **Command Support**: txAdmin REST administrative API commands (`say`, `quit`, console commands).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: CitizenFX resource system (Lua / C# / JavaScript)
- **Mod Directory Path**: `resources`
- **Workshop Synchronization**: Manual volume management and resource downloading.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "quit"
  ```
- **Signal Handling**: Entrypoint catches `SIGTERM` / `SIGINT` to gracefully terminate `fxserver` and flush embedded MariaDB data before pod teardown.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches container non-root user (`gameplane`).
- **Environment**: `spec.env` specifies `HOME: /home/gameplane`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` guarantees read/write access to `/server-data`.
- **Diagnostic Idle**: Graceful idle without crash-looping if `CFX_LICENSE_KEY` is missing (FR-013).

---

## 9. References & Upstream Documentation

- Official Documentation: https://docs.fivem.net/docs/server-manual/setting-up-a-server/
- txAdmin Documentation: https://aka.cfx.re/txAdmin
- Cfx.re Keymaster: https://keymaster.fivem.net
