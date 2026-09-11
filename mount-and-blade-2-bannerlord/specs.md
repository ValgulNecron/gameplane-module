# Gameplane Module Specification: Mount & Blade II: Bannerlord

## 1. Purpose & Scope

- **Game**: Mount & Blade II: Bannerlord
- **Module Slug**: `mount-and-blade-2-bannerlord`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Medieval combat simulation and roleplay multiplayer server. Provides match-based skirmish and siege modes with PTY-attached server administration.

---

## 2. Container Image & Architecture

- **Base Image**: `ghcr.io/valgulnecron/gameplane/mount-and-blade-2-bannerlord:latest@sha256:0000000000000000000000000000000000000000000000000000000000000000`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Linux-native / Wine .NET 6 TaleWorlds dedicated server binary.
- **User & Execution Context**: UID `1000`, GID `1000`, working directory `/serverdata`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `7210` | `UDP` | Client game traffic |
| `query` | `7211` | `UDP` | Server browser and A2S query discovery |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/serverdata`
- **Default Sizing**: `20Gi`
- **Persisted Content**:
  - Downloaded server binaries and TaleWorlds modules
  - Match configuration files (`tdm_config.txt`, `siege_config.txt`)
  - Server tokens and authentication credentials
- **Non-Shadowing Invariant**: Dedicated server install root resides within `/serverdata`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none`
- **Console Mode**: `pty`
- **Authentication**: N/A (interactive stdin console).
- **Command Support**: TaleWorlds CLI console commands issued via stdin.

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Bannerlord Module XMLs and sub-modules
- **Mod Directory Path**: `Modules`
- **Workshop Synchronization**: Manual file drop or volume mount.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**: `[]` (Stateless match-based gameplay; processes terminate cleanly on SIGTERM).
- **Signal Handling**: Container intercepts `SIGTERM` and shuts down the active match cleanly.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user.
- **Environment**: `spec.env` defines `HOME: /serverdata`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` ensures write permission on `/serverdata`.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://www.taleworlds.com/
- Steam Dedicated Server AppID: `1863440`
