# Nuclear Option Module

Nuclear Option is a multiplayer tactical team-based game. This module provides a dedicated server that installs and runs via SteamCMD on Kubernetes.

## Overview

**Game App ID**: 3930080  
**Server Binary**: NuclearOptionServer.x86_64 (Unity, x86_64 only — no arm64 support)  
**Minimum Cluster Resource**: 1 CPU, 2 GiB memory, 2 GiB storage  

The server runs as non-root user `gameserver` (uid/gid 10000) for security.

## Installation

On first pod start, SteamCMD downloads the server (~891 MB) into the data volume. This takes a few minutes; the startup probe budgets ~20 minutes to account for network variability.

## Configuration

The server is configured via a JSON config file (`DedicatedServerConfig.json`) rendered from the **Settings** tab on server creation:

| Field | Description |
|-------|-------------|
| **Server name** | Display name in server lists. |
| **Max players** | Concurrent player limit. Default observed: 16. |
| **Server password** | Password to join; leave blank for open server. |
| **Mission rotation type** | Rotation mode: 0 or 1 (exact semantics unverified; 0 appears sequential). |

## Remote Console

The server exposes a JSON request/response remote-command protocol on TCP port 7779 (loopback-only, no authentication). The agent connects pod-locally.

**20 registered commands** (from spec 002-nuclear-option-ip-pool/contracts):

*Most commonly used*:
- `get-player-list` → `{"Players": [...]}` (player fields: `steamId`, `faction`)
- `send-chat-message <message>` — send broadcast message to all players
- `kick-player <steam-id>`
- `banlist-add <steam-id>` — [optionally `<reason>`]
- `banlist-remove <steam-id>`
- `set-next-mission <Group> <Name> <MaxTime>` — **THREE args** (e.g., `"BuiltIn"`, `"Escalation"`, `"7200.0"`)
- `get-mission` → current + next mission info
- `get-mission-rotation` → rotation config and sequence

*Others*: `reload-config`, `get-mission-time`, `set-time-remaining`, `get-server-id`, `unkick-player`, `clear-kicked-player`, `clear-kicked-players`, `clear-next-mission`, `banlist-reload`, `banlist-clear`, `set-mission-rotation`, `update-ready`.

**Wire Format**:
- **Request**: 4-byte LE length + JSON `{"name": "...", "arguments": [...]}`
- **Response**: 4-byte LE status + 4-byte LE body length + JSON body (if length > 0)
- **Status codes**: 2000 = success, 4003 = JSON error, 4004 = unknown command, 4005 = bad arguments, 5xxx = server errors
- **No authentication**: port is loopback-only; any pod-local client can issue commands

**Critical caveats**:
- `kick-player`, `banlist-add`, `banlist-remove` return 2000 (success) **even for nonexistent Steam IDs**; the command does not fail or signal that the target was found. Verify outcomes by querying player lists or ban lists.
- Display names: `get-player-list` returns only `steamId` and `faction`; the dashboard hydrates display names via Steam Web API on the API server side.

## Ports

| Port | Protocol | Purpose | Advertised | Notes |
|------|----------|---------|-----------|-------|
| 7778 | UDP | Game traffic (inferred) | Yes | Port binding observed during testing; purpose not verified |
| 7779 | TCP | Remote commands | No | Loopback-only (127.0.0.1); pod-local console access only |

**Game Join Port (UDP 7777)**: The server advertises via Steam (SteamGameServer.LogOnAnonymous + "Set Advertise Server: True" in logs) rather than opening a local UDP 7777 port. No dedicated local listen port for game discovery was observed during testing. Players likely join through Steam's game-server routing rather than a raw local port.

## Logs and Persistence

- **Game logs**: stdout (view via `kubectl logs`)
- **Config file**: `/data/DedicatedServerConfig.json` (rendered on every pod start from template)
- **Mission files**: `/data/NuclearOption-Missions/` (persisted across restarts; custom missions placed here)
- **Ban list**: `/data/ban_list.txt` (persisted, managed by the server)

Backups capture the entire `/data` volume, so game config, world state, ban list, and logs all persist.

## Known Limitations

- **No dedicated join port detected**: Live testing on 2026-08-22 found UDP 7778 bound (query port) but **UDP 7777 was NOT observed listening**. The server advertises via Steam (`SteamGameServer.LogOnAnonymous` + `Set Advertise Server: True`), suggesting players join through Steam's game-server routing rather than a raw local UDP port. Join functionality has not been end-to-end verified with an actual client; treat as exploratory.
- **No arm64 support**: The binary is x86_64 only (Linux native, no Proton layer). The module does not run on arm64 clusters.
- **Player list shape partially unverified**: The official protocol spec documents `steamId` and `faction` fields, but this was not confirmed with a live player connected. Display names are not available on the wire; they are hydrated server-side via Steam Web API.

## Version

- **Module version**: 1.0.0
- **Requires Gameplane**: ≥ 0.2.0-beta.7
