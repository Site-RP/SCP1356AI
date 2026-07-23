# SER Methoden — Map

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## CleanupPickups
- Beschreibung: Cleans pickups (items) from the map.
- Argumente: keine
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/MapMethods/CleanupPickupsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CleanupRagdolls
- Beschreibung: Destroys ragdolls.
- Argumente: roleToRemove: Enum<RoleTypeId>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/MapMethods/CleanupRagdollsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CreateRagdoll
- Beschreibung: Spawns a ragdoll.
- Argumente: role: Enum<RoleTypeId>, name: Text, x position: Float, y position: Float, z position: Float, x size: Float, y size: Float, z size: Float, x rotation: Float, y rotation: Float, z rotation: Float, w rotation: Float, damage handler: AnyValue
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/MapMethods/CreateRagdollMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## Decontamination
- Beschreibung: Controls the LCZ decontamination.
- Argumente: mode: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/MapMethods/DecontaminationMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## DecontaminationInfo
- Beschreibung: Returns decontamination info.
- Argumente: option: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/MapMethods/DecontaminationInfoMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GetFromMap
- Beschreibung: Gets a collection of objects from a map.
- Argumente: object: Options
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/MapMethods/GetFromMapMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GetPickups
- Beschreibung: Returns a collection of references to pickups.
- Argumente: keine
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/MapMethods/GetPickupsMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
