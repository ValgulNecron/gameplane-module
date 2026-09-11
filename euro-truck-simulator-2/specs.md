# Gameplane Module Specification: Euro Truck Simulator 2

## 1. Purpose & Scope

- **Game**: Euro Truck Simulator 2
- **Module Slug**: `euro-truck-simulator-2`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated convoy multiplayer server for Euro Truck Simulator 2. Features PTY-driven console management, Steam server logon token configuration, and diagnostic idle for unconfigured deployments.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/euro-truck-simulator-2:latest@sha256:0000000000000000000000000000000000000000000000000000000000000000`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Linux 64-bit standalone dedicated server binary (`eurotrucks2_server`) managed by Gameplane supervisor script.
- **User & Execution Context**: UID `1000`, GID `1000`, working directory `/serverdata`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `27015` | `UDP` | Primary client convoy game traffic |
| `query` | `27016` | `UDP` | Steam server browser query |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/steam/.local/share/Euro Truck Simulator 2`
- **Default Sizing**: `10Gi`
- **Persisted Content**:
  - Convoy configuration files (`server_config.sii`)
  - Server packages, saves, and session cache
- **Non-Shadowing Invariant**: Mount path isolates user profile state without shadowing the server binary in `/serverdata`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none`
- **Console Mode**: `pty`
- **Authentication**: N/A (interactive terminal console).
- **Command Support**: Standard ETS2 server console commands issued via stdin.

---

## 6. Modding & Workshop Integration

- **Modding Framework**: SCS packages and Steam Workshop convoy mods
- **Mod Directory Path**: Mod packages placed in profile directory
- **Workshop Synchronization**: Handled via convoy session sync.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "exit"
  ```
- **Signal Handling**: Issues `exit` to stdin and catches `SIGTERM` in `entrypoint.sh` for clean termination.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user.
- **Environment**: `spec.env` defines `HOME: /home/gameplane`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` guarantees write permissions.
- **Diagnostic Idle**: Automatically enters idle state with step-by-step instructions if `SERVER_LOGON_TOKEN` is missing (FR-013).

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://eurotrucksimulator2.com/
- Steam Dedicated Server AppID: `1948400`
