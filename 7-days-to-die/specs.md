# Gameplane Module Specification: 7 Days to Die

## 1. Purpose & Scope

- **Game**: 7 Days to Die
- **Module Slug**: `7-days-to-die`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Voxel-based open-world zombie survival crafting dedicated server. Backed by LinuxGSM-powered `vinanrra/7dtd-server`, with dual persistent storage for world saves and game files.

---

## 2. Container Image & Architecture

- **Base Image**: `vinanrra/7dtd-server:latest@sha256:0aa521d9660cba22bb42d515a815bb08a18357a7da931ee805c8fcfa1e793910`
- **Architecture**: `linux/amd64`
- **Runtime Model**: LinuxGSM runner executing 7 Days to Die Unity dedicated server binaries with automated updates via SteamCMD.
- **User & Execution Context**: Starts as root to run entrypoint scripts and drops privileges to LinuxGSM user `sdtdserver` (UID `1000`). Working directory `/home/sdtdserver`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `26900` | `TCP` | Main game connection port |
| `game-udp` | `26900` | `UDP` | Game traffic and client discovery |
| `game2` | `26901` | `UDP` | Auxiliary game traffic |
| `game3` | `26902` | `UDP` | Auxiliary game traffic |
| `telnet` | `8081` | `TCP` | Internal Telnet administrative port (unmanaged) |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/sdtdserver/.local/share/7DaysToDie`
- **Default Sizing**: `10Gi` (world saves) + `45Gi` (`extra` volume for `serverfiles`)
- **Persisted Content**:
  - Generated worlds and player data (`/home/sdtdserver/.local/share/7DaysToDie/Saves`)
  - Server install and binaries (`/home/sdtdserver/serverfiles`)
- **Non-Shadowing Invariant**: Does not mount directly over `/home/sdtdserver`, preserving the container entrypoint launcher script (`user.sh`).

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none` (Telnet password is baked in `serverconfig.xml` under `serverfiles/`; no environment injection supported).
- **Console Mode**: `none`
- **Authentication**: N/A
- **Command Support**: N/A

---

## 6. Modding & Workshop Integration

- **Modding Framework**: LinuxGSM script mod installers (Undead Legacy, Darkness Falls, Alloc's Server Fixes)
- **Mod Directory Path**: Handled at container start via `scripts/Mods/*.sh`
- **Workshop Synchronization**: Config-driven URLs via `MODS_URLS`

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**: `[]` (Empty; no RCON reachable).
- **Signal Handling**: Container traps `SIGINT` / `SIGTERM` and triggers `sdtdserver stop` to perform clean world save.

---

## 8. Key Invariants & Security

- **Dual Volume Mount**: Separate mounts for `.local/share/7DaysToDie` (saves) and `serverfiles` (game) avoid shadowing the entrypoint.
- **Filesystem Permissions**: LinuxGSM drops root privileges; storage permissions are maintained across restarts.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://7daystodie.com/
- Upstream Container Repository: https://github.com/vinanrra/Docker-7DaysToDie
- Steam Dedicated Server AppID: `294420`
