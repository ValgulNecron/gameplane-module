# Gameplane Module Specification: Terraria

## 1. Purpose & Scope

- **Game**: Terraria
- **Module Slug**: `terraria`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: 2D action-adventure sandbox multiplayer server. Supports both vanilla worlds and tModLoader modded instances with interactive PTY console access and auto-saving world management.

---

## 2. Container Image & Architecture

- **Base Image**: `passivelemon/terraria-docker:terraria-latest@sha256:d60f280522d6c71079638b5036bdd6c4ac9f93c9f3250477ddb345fc2c6933f3`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Standalone .NET 6 runtime server extracted and executed directly within container.
- **User & Execution Context**: Root container execution (`/opt/terraria`).

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `7777` | `TCP` | Primary client game connection |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/opt/terraria/config`
- **Default Sizing**: `4Gi`
- **Persisted Content**:
  - Saved world files (`Worlds/*.wld`)
  - Server configuration files (`serverconfig.txt`)
  - Banlists and player records
  - tModLoader modpacks (`ModPacks/`)
- **Non-Shadowing Invariant**: Mount path isolates user config and world saves without shadowing the container's `/opt/terraria` binary installation.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none`
- **Console Mode**: `pty`
- **Authentication**: N/A (interactive stdin/stdout console).
- **Command Support**: Standard Terraria CLI commands (`say`, `save`, `kick`, `ban`, `settle`, `motd`, `dawn`, `noon`, `dusk`, `midnight`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: tModLoader modpacks (selected via version catalog)
- **Mod Directory Path**: `ModPacks` (extensions: `.zip`, `.tmod`)
- **Workshop Synchronization**: Manual upload and modpack selection via `MODPACK` config field.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "exit"
  ```
- **Signal Handling**: Injects `exit` to stdin to trigger the engine's built-in world save before terminating.

---

## 8. Key Invariants & Security

- **Network Wake Protocol**: Declares `wakeProtocol: terraria` under `spec.ports[game]` to allow wake-on-traffic.
- **Readiness Probe**: Uses TCP socket probe against port `7777`.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://terraria.org/
- Upstream Container Repository: https://github.com/PassiveLemon/terraria-docker
- Steam Dedicated Server AppID: `105600`
