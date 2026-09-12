# Gameplane Module Specification: BeamMP

## 1. Purpose & Scope

- **Game**: BeamNG.drive (BeamMP Multiplayer)
- **Module Slug**: `beammp`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated multiplayer server for BeamNG.drive soft-body vehicle physics simulation. Features custom vehicle/map mod loading and non-crashing diagnostic idle when the auth key is missing.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/beammp:latest@sha256:0000000000000000000000000000000000000000000000000000000000000000`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Standalone C++ binary (`BeamMP-Server`) executing natively under Alpine Linux.
- **User & Execution Context**: UID `1000`, GID `1000`, working directory `/serverdata`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `30814` | `UDP` | Primary client physics packet stream |
| `auth` | `30814` | `TCP` | Client authentication and TCP sync |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/server/Root`
- **Default Sizing**: `5Gi`
- **Persisted Content**:
  - `ServerConfig.toml` configuration
  - Custom vehicles, levels, and track mods (`Resources/`)
- **Non-Shadowing Invariant**: The mount path `/server/Root` is symlinked to `/serverdata` and does not shadow the application binary in `/opt/beammp`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none`
- **Console Mode**: `pty`
- **Authentication**: N/A (interactive terminal console).
- **Command Support**: Standard BeamMP CLI commands issued via stdin.

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Custom vehicle and map `.zip` archives
- **Mod Directory Path**: `Resources`
- **Workshop Synchronization**: Manual file drop or archive upload via Gameplane Mods tab.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**: `[]` (Stateless vehicle session; processes terminate cleanly on SIGTERM).
- **Signal Handling**: Container intercepts `SIGTERM` / `SIGINT` and halts `BeamMP-Server` process cleanly.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user.
- **Environment**: `spec.env` defines `HOME: /home/gameplane`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` guarantees write permission on `/server/Root`.
- **Diagnostic Idle**: Graceful idle without crash-looping if `BEAMMP_AUTH_KEY` is missing (FR-013).

---

## 9. References & Upstream Documentation

- Official Website: https://beammp.com/
- Server Documentation: https://wiki.beammp.com/en/home/server-installation
