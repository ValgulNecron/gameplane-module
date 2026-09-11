# Gameplane Module Specification: Don't Starve Together

## 1. Purpose & Scope

- **Game**: Don't Starve Together
- **Module Slug**: `dont-starve-together`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Dedicated multiplayer server for Klei Entertainment's Don't Starve Together, supporting master and caves multi-shard architecture.

---

## 2. Container Image & Architecture

- **Base Image**: `jamesits/dst-server:vanilla@sha256:fa61065f8d2d770bc5d45f1a160b87b1deada3fd5903d9524b771321ca98dc58`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Standalone binary / Wine-free Linux server running Master and Caves shards.
- **User & Execution Context**: UID 1000, working directory `/data`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | 10999 | UDP | Primary master shard game port |
| `query` | 27018 | UDP | Steam browser query port |
| `caves` | 11000 | UDP | Caves shard game port |
| `steam1` | 12346 | UDP | Steam internal communication |
| `steam2` | 12347 | UDP | Steam internal communication |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/data`
- **Default Sizing**: `5Gi`
- **Persisted Content**:
  - Cluster settings and server tokens (`Cluster_1/cluster.ini`, `cluster_token.txt`)
  - Master shard world state and player records (`Cluster_1/Master/save`)
  - Caves shard subterranean state (`Cluster_1/Caves/save`)
- **Non-Shadowing Invariant**: The mount path isolates cluster state under `/data`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `none`
- **Console Mode**: `pty` (Lua command evaluation over container stdin)
- **Authentication**: N/A (local container stdin)
- **Command Support**: DST Lua console functions (`c_announce`, `c_save`, `c_rollback`, `c_regenerateworld`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: Steam Workshop / Klei dedicated server mod setup (`dedicated_server_mods_setup.lua`).
- **Mod Directory Path**: Handled inside `/data`.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "c_save()"
        - "c_shutdown(true)"
  ```
- **Signal Handling**: Dedicated server responds to stdin Lua commands for clean world persistence.

---

## 8. Key Invariants & Security

- **User Matching**: Default image unprivileged execution.
- **Filesystem Permissions**: Persistent storage mounted at `/data`.

---

## 9. References & Upstream Documentation

- Klei Dedicated Server Hosting Guide: https://dontstarve.fandom.com/wiki/Guides/Don%E2%80%99t_Starve_Together_Dedicated_Servers
- Upstream Container Repository: https://github.com/Jamesits/docker-dst-server
- Steam Dedicated Server AppID: 343050
