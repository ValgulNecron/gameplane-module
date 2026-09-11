# Gameplane Module Specification: Factorio (Headless)

## 1. Purpose & Scope

- **Game**: Factorio
- **Module Slug**: `factorio`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated headless server package for Factorio, Wube Software's automation and factory simulation game. Runs standalone headless binary inside the image, loading saves, configuration, and mods from persistent storage.

---

## 2. Container Image & Architecture

- **Base Image**: `factoriotools/factorio:stable@sha256:7052b3cca8ca7790f99f4058617d5c8089df544de736b1baa23f2c5f58fb7f48`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Standalone binary packaged inside container image (no SteamCMD required).
- **User & Execution Context**: factorio user (`factorio`), UID/GID managed within image.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 34197 | UDP | Primary gameplay traffic |
| `rcon` | 27015 | TCP | Source RCON protocol port (used for probes and actions) |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/factorio`
- **Default Sizing**: `5Gi`
- **Persisted Content**:
  - Saved games (`/factorio/saves`)
  - Server configuration and settings (`/factorio/config`)
  - Mods directory (`/factorio/mods`)
- **Non-Shadowing Invariant**: The mount path encompasses data directories managed by the container entrypoint.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source` (with `consoleMode: pty`)
- **Console Mode**: `pty` (attaches to container stdin for direct command execution; RCON port available for operator automation)
- **Authentication**: `config/rconpw` file on storage volume.
- **Command Support**: In-game moderation (`/kick`, `/ban`, `/unban`, `/mute`), manual saving (`/save`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Native Factorio mod portal zip packages.
- **Mod Directory Path**: `mods`
- **Registry Integration**: Official Factorio Mod Portal browser.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "/server-save"
  ```
- **Signal Handling**: Factorio traps `SIGINT`/`SIGTERM` and initiates an automatic flush to disk before exiting.

---

## 8. Key Invariants & Security

- **User Matching**: Default unprivileged container execution.
- **Filesystem Permissions**: Volume ownership managed for `/factorio`.

---

## 9. References & Upstream Documentation

- Factorio Multiplayer Server Documentation: https://wiki.factorio.com/Multiplayer
- Upstream Container Repository: https://github.com/factoriotools/factorio-docker
