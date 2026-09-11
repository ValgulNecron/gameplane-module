# Gameplane Module Specification: DayZ

## 1. Purpose & Scope

- **Game**: DayZ
- **Module Slug**: `dayz`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Post-apocalyptic persistent multiplayer survival game powered by Bohemia Interactive's Enfusion/Real Virtuality engine. Features BattlEye RCon remote console and Steam Workshop mod synchronization.

---

## 2. Container Image & Architecture

- **Base Image**: `registry.godbleak.dev/godbleak/serverz:latest@sha256:5e8757beae763c862d08a9c08587c35211cda74ce399f7419492d7520adab4fe`
- **Architecture**: `linux/amd64`
- **Runtime Model**: SteamCMD Linux dedicated server runner with Proton/Wine emulation layer managed by GodBleak/ServerZ wrapper.
- **User & Execution Context**: Starts as root, manages runtime directories `/data`, `/install`, `/overrides`. Working directory `/`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `2302` | `UDP` | Primary client game traffic |
| `query` | `27015` | `UDP` | Steam A2S server query |
| `rcon` | `2305` | `UDP` | BattlEye RCon administrative protocol |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/data`
- **Default Sizing**: `40Gi`
- **Persisted Content**:
  - World saves and player hive data (`/data`)
  - Server profile state and mission files
- **Non-Shadowing Invariant**: Mount path `/data` holds server state without shadowing `/install` or entrypoint launcher scripts.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `battleye` (BattlEye RCon over UDP)
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via `spec.rcon.passwordEnv: BE_PASSWORD` (written to `beserver_x64.cfg`).
- **Command Support**: BattlEye RCon commands (`players`, `say -1 <msg>`, `#kick <number>`, `#lock`, `#unlock`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: DayZ Steam Workshop mods
- **Mod Directory Path**: Handled natively via `MOD_LIST` SteamCMD workshop synchronization.
- **Workshop Synchronization**: Config-driven item IDs downloaded at startup.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**: `[]` (Empty list; DayZ continuously flushes hive data and relies on graceful `SIGTERM` trap handling).
- **Signal Handling**: Container intercepts `SIGTERM` and shuts down server process cleanly without data corruption.

---

## 8. Key Invariants & Security

- **Network Security**: BattlEye RCon binds to loopback (`127.0.0.1:2305`) so that only the in-pod Gameplane agent sidecar can connect, preventing public network brute-forcing.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://dayz.com/
- Upstream Container Repository: https://github.com/GodBleak/ServerZ
- Steam Dedicated Server AppID: `223350`
