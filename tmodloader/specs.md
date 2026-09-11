# Gameplane Module Specification: tModLoader

## 1. Purpose & Scope

- **Game**: tModLoader (Terraria Modding Framework)
- **Module Slug**: `tmodloader`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Modded Terraria dedicated server running the tModLoader .NET 6 framework. Supports `.tmod` community mods, custom modpacks, and PTY-attached server administration.

---

## 2. Container Image & Architecture

- **Base Image**: `passivelemon/terraria-docker:tmodloader-latest@sha256:3f2d8703421159f1037084bd2c0901a3a63b85a00801cf36f6f928e8b666b44e`
- **Architecture**: `linux/amd64`
- **Runtime Model**: .NET 6 runtime host running `tModLoader.dll` with integrated mono/native runtime dependencies.
- **User & Execution Context**: Root container execution (`/`).

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `7777` | `TCP` | Main client game traffic |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/root/.local/share/Terraria/tModLoader`
- **Default Sizing**: `4Gi`
- **Persisted Content**:
  - Generated modded worlds (`Worlds/*.wld`)
  - Downloaded `.tmod` mod archives (`Mods/`)
  - Server config, mod configs, and banlists
- **Non-Shadowing Invariant**: Mounted path preserves `/opt/terraria` binary installation and launcher scripts.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none`
- **Console Mode**: `pty`
- **Authentication**: N/A (interactive terminal console).
- **Command Support**: Standard Terraria and tModLoader CLI commands (`say`, `save`, `exit`, mod reload commands).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: tModLoader Mod System (`.tmod` packages)
- **Mod Directory Path**: `Mods`
- **Workshop Synchronization**: Manual install and URL download via Gameplane Mods tab.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "exit"
  ```
- **Signal Handling**: Issues `exit` to stdin for orderly world saving prior to termination.

---

## 8. Key Invariants & Security

- **Wake-On-Traffic**: Declares `wakeProtocol: terraria` under `spec.ports[game]`.
- **Readiness Probe**: Uses TCP probe on port `7777`.

---

## 9. References & Upstream Documentation

- Official Documentation: https://www.tmodloader.net/
- Upstream Container Repository: https://github.com/PassiveLemon/terraria-docker
- Steam Dedicated Server AppID: `1281930`
