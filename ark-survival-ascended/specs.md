# Gameplane Module Specification: ARK: Survival Ascended

## 1. Purpose & Scope

- **Game**: ARK: Survival Ascended
- **Module Slug**: `ark-survival-ascended`
- **Role**: Dedicated server module package for Gameplane.
- **Description**: Unreal Engine 5 dinosaur survival multiplayer dedicated server. Powered by `mschnitzer/asa-linux-server`, supporting crossplay, CurseForge modding, cluster travel, and Source RCON administration.

---

## 2. Container Image & Architecture

- **Base Image**: `mschnitzer/asa-linux-server:latest@sha256:0d69614f24da77e208b0ad453e1f5791fe2786fb8860269f8df5c26b527848f9`
- **Architecture**: `linux/amd64`
- **Runtime Model**: Wine/Proton execution of the Windows/Linux UE5 dedicated server binary with SteamCMD synchronization at container startup.
- **User & Execution Context**: Image user `gameserver` (UID `25000`), working directory `/home/gameserver`.

---

## 3. Network Ports & Protocols

Declared ports under `spec.ports`:

| Port Name | Container Port | Protocol | Usage / Purpose |
|---|---|---|---|
| `game` | `7777` | `UDP` | Primary client game traffic |
| `peer` | `7778` | `UDP` | Peer / raw UDP communication |
| `rcon` | `27020` | `TCP` | Source RCON administrative console |

---

## 4. Storage & Persistence Layout

- **Mount Path**: `/home/gameserver`
- **Default Sizing**: `30Gi`
- **Persisted Content**:
  - Saved worlds and tribe data (`server-files/ShooterGame/Saved/`)
  - Server configuration files (`server-files/ShooterGame/Saved/Config/WindowsServer/GameUserSettings.ini`)
  - Cluster shared travel data (`cluster-shared/`)
  - Steam and SteamCMD caches (`steam-cache/`, `steamcmd-cache/`)
- **Non-Shadowing Invariant**: The volume at `/home/gameserver` hosts user data and steamcmd files; entrypoint binary `/usr/bin/start_server` resides in system path `/usr/bin`.

---

## 5. Administration & Remote Console (RCON)

- **Protocol**: `source`
- **Console Mode**: `rcon`
- **Authentication**: Password supplied via file `rcon-password.txt` or password secret.
- **Command Support**: Standard ARK RCON commands (`SaveWorld`, `DoExit`, `ServerChat`, `KickPlayer`, `BanPlayer`, `DestroyWildDinos`, `SetTimeOfDay`).

---

## 6. Modding & Workshop Integration

- **Modding Framework**: CurseForge ARK mods
- **Mod Directory Path**: Handled via launch argument `-mods=<curseforge-id>,...` appended to `ASA_START_PARAMS`.
- **Workshop Synchronization**: Automatic download by game client at boot via CurseForge API.

---

## 7. Lifecycle & Graceful Shutdown

- **Stop Command Sequence (`spec.capabilities.lifecycle.stop`)**:
  ```yaml
  capabilities:
    lifecycle:
      stop:
        - "SaveWorld"
        - "DoExit"
  ```
- **Signal Handling**: Issues `SaveWorld` and `DoExit` via Source RCON before container terminates, preventing world corruption and rollbacks.

---

## 8. Key Invariants & Security

- **User Matching**: Image runs strictly as UID `25000`. `spec.security.runAsUser: 25000` and `fsGroup: 25000` ensure non-root volume permissions for Proton.
- **Explicit Command**: `spec.command: ["/usr/bin/start_server"]` is declared to avoid non-interactive shell EOF termination.

---

## 9. References & Upstream Documentation

- Official Game Documentation: https://survivetheark.com/
- Upstream Container Repository: https://github.com/mschnitzer/asa-linux-server
- Steam Dedicated Server AppID: `2430930`
