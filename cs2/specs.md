# Gameplane Module Specification: Counter-Strike 2

## 1. Purpose & Scope

- **Game**: Counter-Strike 2
- **Module Slug**: `cs2`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Tactical competitive first-person shooter dedicated server powered by Valve's Source 2 engine. Matches are session-based with optional Metamod / CounterStrikeSharp plugin support and Steam Workshop map rotation.

---

## 2. Container Image & Architecture

- **Base Image**: `joedwards32/cs2:latest@sha256:41b826d6280d1aa9e41c866a6d88cc7f523e027f16c47a313b20c2d7a17f2680`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Native Source 2 Linux dedicated server binary fetched and updated via SteamCMD.
- **User & Execution Context**: UID `1000`, GID `1000`, working directory `/home/steam/cs2-dedicated`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `27015` | `UDP` | Primary client game traffic & Steam server queries |
| `rcon` | `27015` | `TCP` | Source RCON administrative console |
| `gotv` | `27020` | `UDP` | SourceTV / GOTV spectator relay broadcast |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/steam/cs2-dedicated`
- **Default Sizing**: `60Gi` (minimum installation requirement for base game + updates)
- **Persisted Content**:
  - Downloaded Source 2 dedicated server binaries and assets
  - Server configurations (`game/csgo/cfg/server.cfg`)
  - Workshop map cache and downloaded addons
  - Metamod / CounterStrikeSharp plugins (`game/csgo/addons`)
- **Non-Shadowing Invariant**: Mounted volume contains the dedicated server root install directory created at runtime; does not shadow container base OS or entrypoint.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source`
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `spec.rcon.passwordEnv: CS2_RCONPW`.
- **Command Support**: Standard Valve Source RCON console commands (e.g., `say`, `mp_restartgame`, `changelevel`, `exec`, `bot_add`, `bot_kick`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Metamod:Source and CounterStrikeSharp (CoreCLR)
- **Mod Directory Path**: `game/csgo/addons` (extensions: `.dll`, `.so`)
- **Workshop Synchronization**: Steam Workshop collections configured via `CS2_HOST_WORKSHOP_COLLECTION` and downloaded natively by `srcds` at startup.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "quit"
  ```
- **Signal Handling**: Exits cleanly upon `quit` command without lingering on active match rounds. Container traps signals for shutdown.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user (`1000`).
- **Environment**: `spec.env` specifies `HOME: /home/steam` to allow SteamCMD to locate credentials and configuration without falling back to `//Steam`.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` ensures non-root write access to the mounted persistent volume.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://www.counter-strike.net/cs2
- Upstream Container Repository: https://github.com/joedwards32/CS2
- Steam Dedicated Server AppID: `730`
