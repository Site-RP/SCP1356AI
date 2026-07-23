# SER Methoden — Pickup

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## AddPickupToInventory
- Beschreibung: Forces a pickup to be added to the player's inventory.
- Argumente: player: Player, pickup: Reference<Pickup>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PickupMethods/AddPickupToInventoryMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CreateGrenade
- Beschreibung: Creates a new grenade projectile to later spawn.
- Argumente: grenade type: Options, attacker: Player
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PickupMethods/CreateGrenadeMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CreatePickup
- Beschreibung: Creates a new item pickup to later spawn.
- Argumente: item type: Enum<ItemType>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PickupMethods/CreatePickupMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DestroyPickup
- Beschreibung: Destroys a pickup / grenade from the map.
- Argumente: pickup/projectile reference: Reference<Pickup>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PickupMethods/DestroyPickupMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## PickupExists
- Beschreibung: Returns true if the provided pickup is still present on the server.
- Argumente: pickup reference: Reference<Pickup>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PickupMethods/PickupExistsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SpawnPickupPlayer
- Beschreibung: Spawns an item pickup / grenade on a player.
- Argumente: pickup/projectile reference: Reference<Pickup>, player to spawn pickup on: Player
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PickupMethods/SpawnPickupPlayerMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SpawnPickupPos
- Beschreibung: Spawns an item pickup / grenade at the coordinates.
- Argumente: pickup/projectile reference: Reference<Pickup>, x position: Float, y position: Float, z position: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PickupMethods/SpawnPickupPosMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SpawnPickupRoom
- Beschreibung: Spawns an item pickup / grenade in a room.
- Argumente: pickup/projectile reference: Reference<Pickup>, room to spawn pickup in: Room, relative x: Float, relative y: Float, relative z: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/PickupMethods/SpawnPickupRoomMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
