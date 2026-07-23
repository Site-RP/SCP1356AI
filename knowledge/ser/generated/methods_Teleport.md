# SER Methoden — Teleport

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## TPDoor
- Beschreibung: Teleports players to a door.
- Argumente: players to teleport: Players, door to teleport to: Door
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TeleportMethods/TPDoorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## TPPlayer
- Beschreibung: Teleports players to another player.
- Argumente: players to TP: Players, player target: Player
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TeleportMethods/TPPlayerMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## TPPosition
- Beschreibung: Teleports players to an XYZ position.
- Argumente: players to TP: Players, X coordinate: Float, Y coordinate: Float, Z coordinate: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TeleportMethods/TPPositionMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## TPRoom
- Beschreibung: Teleports players to relative coordinates of a room.
- Argumente: players to teleport: Players, room to teleport to: Room, relative x: Float, relative y: Float, relative z: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TeleportMethods/TPRoomMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## TPSpawn
- Beschreibung: Teleports players to where a specified role would spawn.
- Argumente: players to teleport: Players, spawnpoint of role: Enum<RoleTypeId>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/TeleportMethods/TPSpawnMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
