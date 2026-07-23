# SER Methoden — Door

> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.

## BreakDoor
- Beschreibung: Breaks specified doors if possible.
- Argumente: doors: Doors, damage type: Enum<DoorDamageType>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/BreakDoorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## CloseDoor
- Beschreibung: Closes doors.
- Argumente: doors: Doors
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/CloseDoorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## GetRandomDoor
- Beschreibung: Returns a reference to a random door.
- Argumente: keine
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/GetRandomDoorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## LockDoor
- Beschreibung: Locks doors.
- Argumente: doors: Doors, lock: Enum<DoorLockReason>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/LockDoorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## OpenDoor
- Beschreibung: Opens doors.
- Argumente: doors: Doors
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/OpenDoorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## PryGate
- Beschreibung: Pries a gate.
- Argumente: gate: Gate, should play effects: Bool
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/PryGateMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## RepairDoor
- Beschreibung: Repairs specified doors if possible
- Argumente: doors to repair: Doors
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/RepairDoorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetDoorHealth
- Beschreibung: Sets remaining health for specified doors if possible
- Argumente: doors: Doors, health: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/SetDoorHealthMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetDoorMaxHealth
- Beschreibung: Sets max health for specified doors if possible
- Argumente: doors: Doors, max health: Float
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/SetDoorMaxHealthMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## SetDoorPermission
- Beschreibung: Sets door permissions.
- Argumente: doors: Doors, permissions: Enum<DoorPermissionFlags>
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/SetDoorPermissionMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.

## UnlockDoor
- Beschreibung: Unlocks doors.
- Argumente: doors: Doors
- Aliases: keine
- Quelle: `Code/MethodSystem/Methods/DoorMethods/UnlockDoorMethod.cs`
- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.
