# Gameplane Module Specification: Left 4 Dead 2

## 1. Purpose & Scope

- **Game**: Left 4 Dead 2
- **Module Slug**: `left-4-dead-2`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated server package for Left 4 Dead 2, Valve's cooperative first-person shooter. Runs on the Source Engine with matchmaking, campaign/versus modes, and SourceMod extension support.

---

## 2. Container Image & Architecture

- **Base Image**: `left4devops/l4d2:latest@sha256:66af49bae4f6a615393001078330196f565e9c8bd1d0eacdaf73cd923b3572c3`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD-based Source Engine dedicated server (`srcds_linux`).
- **User & Execution Context**: UID 1000, GID 1000, working directory `/home/steam`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 27015 | UDP | Primary client gameplay traffic |
| `query` | 27015 | UDP | Server browser discovery and Steam A2S_INFO protocol |
| `rcon` | 27015 | TCP | Remote administrative console (Source RCON) |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/steam/l4d2-dedicated`
- **Default Sizing**: `15Gi`
- **Persisted Content**:
  - Downloaded game binaries, maps, and server configurations (`server.cfg`)
  - Campaign add-ons and custom VPK files
  - Ban lists and player logs
- **Non-Shadowing Invariant**: The mount path does not shadow entrypoint scripts in `/home/steam`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source`
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `RCON_PASSWORD` environment variable.
- **Command Support**: In-game moderation (`kick`, `banid`), map changes (`changelevel`), and announcements (`say`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: SourceMod / MetaMod:Source, custom campaign VPKs.
- **Mod Directory Path**: `left4dead2/addons`
- **Workshop Synchronization**: Manual or automated VPK downloading.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "quit"
  ```
- **Signal Handling**: Dedicated server responds to `SIGINT`/`SIGTERM` and initiates clean shutdown.

---

## 8. Key Invariants & Security

- **User Matching**: `spec.security.runAsUser: 1000` matches image user (`steam`).
- **Environment**: `spec.env` contains `HOME=/home/steam` for SteamCMD runtime.
- **Filesystem Permissions**: `spec.security.fsGroup: 1000` configured for volume permission mapping.

---

## 9. References & Upstream Documentation

- Valve Developer Community L4D2 Dedicated Server: https://developer.valvesoftware.com/wiki/Left_4_Dead_2/Dedicated_Servers
- Upstream Container Repository: https://github.com/left4devops/l4d2
- Steam Dedicated Server AppID: 222860
