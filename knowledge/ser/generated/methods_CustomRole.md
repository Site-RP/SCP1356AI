# SER Methoden — CustomRole

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## CRole.CreateBracketSpawnSystem
- Beschreibung: Creates a spawn for a custom roles that uses ranges of available players.
- Argumente: role to replace: Enum<RoleTypeId>, spawn brackets: Reference<SpawnBracket>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_CreateBracketSpawnSystemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CRole.CreateChanceSpawnSystem
- Beschreibung: Creates a spawn system for a custom role using a simple chance.
- Argumente: role to replace: Enum<RoleTypeId>, replacement chance: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_CreateChanceSpawnSystemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CRole.CreateProceduralSpawnSystem
- Beschreibung: Creates a procedural spawn system for a custom role.
- Argumente: role to replace: Enum<RoleTypeId>, per-player spawn chance: Float, conversion limit: Int, minimum required players: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_CreateProceduralSpawnSystemMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CRole.CreateSpawnBracket
- Beschreibung: Creates a spawn bracket for a the bracket spawn system.
- Argumente: lower bound: Int, upper bound: Int, amount to spawn: Int
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_CreateSpawnBracketMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CRole.IsRegistered
- Beschreibung: Checks if a given custom role is registered.
- Argumente: role id: Text
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_IsRegisteredMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CRole.Register
- Beschreibung: Registers a custom role.
- Argumente: id: Text, display name: Text, role type: Enum<RoleTypeId>, spawn system: Reference<CustomRoleSpawnSystem>, remove role on death: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_RegisterMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CRole.Set
- Beschreibung: Assigns a custom role to a player.
- Argumente: players: Players, custom role: CustomRole
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_SetMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CRole.SetCallbacks
- Beschreibung: Sets the callbacks for a provided custom role.
- Argumente: custom role: CustomRole, on spawning: Callback, on removing: Callback
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_SetCallbacksMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CRole.Unregister
- Beschreibung: Unregisters a given custom role from the server.
- Argumente: custom role: CustomRole
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/CustomRoleMethods/CRole_UnregisterMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
