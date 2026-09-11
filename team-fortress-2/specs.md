# Gameplane Module Specification: Team Fortress 2

## 1. Purpose & Scope

- **Game**: Team Fortress 2
- **Module Slug**: `team-fortress-2`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Team-based multiplayer first-person shooter powered by Valve's Source engine. Session-based gameplay with Source RCON management, SourceMod plugin support, and persistent server installation.

---

## 2. Container Image & Architecture

- **Base Image**: `cm2network/tf2:latest@sha256:39c03ecbee022350a13aec49c7948263c00b5a0d5874b72faf0f4193de863e7b`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Native Linux `srcds_run` dedicated server binary updated via SteamCMD.
- **User & Execution Context**: UID `1000`, GID `1000`, working directory `/home/steam`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `27015` | `UDP` | Client game traffic and A2S discovery queries |
| `rcon` | `27015` | `TCP` | Source RCON remote console |
| `sourcetv` | `27020` | `UDP` | SourceTV spectator relay broadcast |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/steam/tf-dedicated`
- **Default Sizing**: `15Gi`
- **Persisted Content**:
  - Dedicated server game files (`tf/`)
  - Server configurations (`tf/cfg/server.cfg`, mapcycle)
  - Custom maps and SourceMod addons (`tf/maps/`, `tf/addons/`)
- **Non-Shadowing Invariant**: Volume mounts at `/home/steam/tf-dedicated` which preserves the container's `/home/steam/entry.sh` and base files.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source`
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `spec.rcon.passwordEnv: SRCDS_RCONPW`.
- **Command Support**: Valve Source RCON commands (`say`, `changelevel`, `mp_restartgame`, `exec`, `status`, `kick`, `ban`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: MetaMod:Source and SourceMod (`.smx` plugins)
- **Mod Directory Path**: `tf/addons`
- **Workshop Synchronization**: Steam Workshop maps via mapcycle / start map parameters.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "quit"
  ```
- **Signal Handling**: Issues `quit` over Source RCON to cleanly disconnect clients before pod scale down.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user (`steam`).
- **Environment**: `spec.env` defines `HOME: /home/steam`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` guarantees non-root write access to the mounted volume.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://www.teamfortress.com/
- Upstream Container Repository: https://github.com/CM2Walki/TF2
- Steam Dedicated Server AppID: `232250`
